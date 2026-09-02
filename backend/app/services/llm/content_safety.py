import json

from app.services.llm.client import (
    client,
    NVIDIA_SAFETY_MODEL,
)


SAFETY_SYSTEM_PROMPT = """
You are the RecoveryOS customer-message safety validator.

Your job is to evaluate a customer-facing payment
recovery message before it is shown to a customer.

Check whether the message is appropriate for a
payment recovery workflow.

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

Return ONLY valid JSON:

{
    "safe": true,
    "reason": "..."
}

or

{
    "safe": false,
    "reason": "..."
}
"""


def validate_customer_message(
    message: str,
) -> dict:

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
    )

    try:

        result = json.loads(
            content.strip()
        )

    except json.JSONDecodeError:

        return {
            "safe": False,
            "reason": (
                "Content safety model returned "
                "invalid JSON."
            ),
        }

    safe = result.get(
        "safe",
        False,
    )

    reason = result.get(
        "reason",
        "No safety reason provided.",
    )

    return {
        "safe": bool(safe),
        "reason": str(reason),
    }