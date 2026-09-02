import json

from app.services.llm.client import (
    client,
    NVIDIA_MODEL,
)


SYSTEM_PROMPT = """
You are the RecoveryOS Revenue Recovery Analyst.

Analyze the supplied RecoveryOS case.

Your responsibilities:

1. Identify the likely root cause.
2. Explain the revenue at risk.
3. Assess the existing ML prediction.
4. Assess the deterministic recovery policy.
5. Explain the recovery strategy.
6. Generate a concise customer-facing recovery message.

Rules:

- Use only facts supplied in the context.
- Never invent customer information.
- Never invent payment information.
- Never invent recovery outcomes.
- Never override the deterministic policy.
- Never execute financial actions.
- Treat ML probability as an input, not absolute truth.
- If information is unavailable, say so.
- If the case is already recovered, explain the completed outcome.
- If the case is not eligible for recovery, do not recommend executing an action.

Return ONLY a JSON object.
Do not use Markdown.
Do not wrap the JSON in ```.

Required fields:

summary
root_cause
revenue_risk
ml_assessment
policy_assessment
recovery_strategy
customer_message
"""


def _parse_json_response(
    content: str,
) -> dict:

    content = content.strip()

    # Normal JSON response.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Handle ```json ... ``` responses.
    if content.startswith("```"):
        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # Handle accidental surrounding text.
    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        try:
            return json.loads(
                content[start:end + 1]
            )
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "NVIDIA returned invalid JSON."
    )


def analyze_recovery_case(
    context: dict,
) -> dict:

    response = client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    context,
                    default=str,
                ),
            },
        ],
        temperature=1.0,
        top_p=0.95,
        max_tokens=2048,
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

    result = _parse_json_response(
        content
    )

    required_fields = [
        "summary",
        "root_cause",
        "revenue_risk",
        "ml_assessment",
        "policy_assessment",
        "recovery_strategy",
        "customer_message",
    ]

    for field in required_fields:

        if field not in result:
            result[field] = ""

    return result