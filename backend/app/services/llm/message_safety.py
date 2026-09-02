from app.services.llm.content_safety import (
    validate_customer_message,
)


SAFE_FALLBACK_MESSAGE = (
    "We couldn't complete your payment. "
    "Please try again using an available payment "
    "method or contact your bank if the problem continues."
)


def make_safe_customer_message(
    message: str,
) -> dict:

    validation = validate_customer_message(
        message
    )

    if validation["safe"]:

        return {
            "message": message,
            "safe": True,
            "reason": validation["reason"],
            "fallback_used": False,
        }

    return {
        "message": SAFE_FALLBACK_MESSAGE,
        "safe": False,
        "reason": validation["reason"],
        "fallback_used": True,
    }