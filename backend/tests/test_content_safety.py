from unittest.mock import patch

from app.services.llm.message_safety import (
    make_safe_customer_message,
)


def test_safe_customer_message_is_returned():

    with patch(
        "app.services.llm.message_safety.validate_customer_message"
    ) as mock_validate:

        mock_validate.return_value = {
            "safe": True,
            "reason": "Message is appropriate.",
        }

        result = make_safe_customer_message(
            "Your payment could not be completed. "
            "Please try another available payment method."
        )

    assert result["safe"] is True
    assert result["fallback_used"] is False
    assert "payment" in result["message"]


def test_unsafe_customer_message_uses_fallback():

    with patch(
        "app.services.llm.message_safety.validate_customer_message"
    ) as mock_validate:

        mock_validate.return_value = {
            "safe": False,
            "reason": "Message contains unsafe content.",
        }

        result = make_safe_customer_message(
            "Unsafe customer message."
        )

    assert result["safe"] is False
    assert result["fallback_used"] is True

    assert (
        result["message"]
        != "Unsafe customer message."
    )

    assert "payment" in result["message"]