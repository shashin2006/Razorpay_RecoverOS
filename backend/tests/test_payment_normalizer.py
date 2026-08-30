from app.services.payment_normalizer import normalize_payment


def test_normalize_failed_payment():

    payload = {
        "event": "payment.failed",
        "entity": "event",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_TW26aCM8EmMX1T",
                    "amount": 50000,
                    "currency": "INR",
                    "method": "netbanking",
                    "status": "failed",
                    "order_id": "order_TW22i3MDm5wwH7",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_step": "payment_authorization",
                    "error_reason": "payment_failed",
                    "error_source": "bank",
                    "error_description": (
                        "Your payment didn't go through."
                    ),
                }
            }
        },
    }

    result = normalize_payment(payload)

    assert result["razorpay_payment_id"] == (
        "pay_TW26aCM8EmMX1T"
    )

    assert result["razorpay_order_id"] == (
        "order_TW22i3MDm5wwH7"
    )

    assert result["amount_minor"] == 50000

    assert result["currency"] == "INR"

    assert result["method"] == "netbanking"

    assert result["status"] == "failed"

    assert result["error_code"] == "BAD_REQUEST_ERROR"

    assert result["error_source"] == "bank"

    assert result["error_step"] == (
        "payment_authorization"
    )