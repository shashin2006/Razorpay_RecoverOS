import json
import re

from app.services.llm.client import (
    client,
    NVIDIA_SAFETY_MODEL,
)


SAFETY_SYSTEM_PROMPT = """
You are the RecoveryOS customer-message safety validator.

Your job is to evaluate a CUSTOMER-FACING payment recovery
message before it is shown to a customer.

The message must:

- Be professional and respectful.
- Avoid threats, harassment, or intimidation.
- Avoid discriminatory or hateful content.
- Avoid sexual or graphic content.
- Avoid manipulation or coercion.
- Avoid requesting sensitive credentials.
- Avoid requesting passwords, OTPs, CVVs, PINs,
  or secret authentication information.
- Avoid making unsupported claims.
- Avoid inventing customer information.
- Avoid guaranteeing payment success.
- Avoid exposing internal ML or system information.
- Avoid instructing the customer to bypass security.

Return ONLY this JSON structure:

{"safe": true, "reason": "brief reason"}

or

{"safe": false, "reason": "brief reason"}
"""


def _extract_json_object(content: str) -> dict | None:
    """
    Safely extract a JSON object even when the model wraps
    it in markdown fences or adds small amounts of text.
    """

    if not content:
        return None

    cleaned = content.strip()

    # First try the ideal case.
    try:
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Remove common markdown code fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    try:
        result = json.loads(cleaned.strip())

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Last parsing attempt:
    # locate the first complete-looking JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = cleaned[start : end + 1]

        try:
            result = json.loads(candidate)

            if isinstance(result, dict):
                return result

        except json.JSONDecodeError:
            pass

    return None


def validate_customer_message(
    message: str,
) -> dict:

    if not message or not message.strip():

        return {
            "safe": False,
            "reason": "Customer message is empty.",
        }

    try:

        response = client.chat.completions.create(
            model=NVIDIA_SAFETY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SAFETY_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "message": message,
                        }
                    ),
                },
            ],
            temperature=0.0,
            max_tokens=300,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                },
            },
        )

        content = (
            response.choices[0]
            .message
            .content
            or ""
        )

    except Exception as exc:

        return {
            "safe": False,
            "reason": (
                "Content safety validation unavailable: "
                f"{type(exc).__name__}."
            ),
        }

    result = _extract_json_object(content)

    if result is None:

        return {
            "safe": False,
            "reason": (
                "Content safety model returned "
                "an invalid response."
            ),
        }

    safe = result.get("safe")

    # Don't allow values such as the string "false"
    # to accidentally become truthy via bool("false").
    if not isinstance(safe, bool):

        return {
            "safe": False,
            "reason": (
                "Content safety model returned "
                "an invalid safety value."
            ),
        }

    reason = result.get(
        "reason",
        "No safety reason provided.",
    )

    return {
        "safe": safe,
        "reason": str(reason),
    }