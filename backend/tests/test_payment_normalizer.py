from app.services.payment_normalizer import normalize_payment


def test_normalize_failed_stripe_payment():
    payload = {
        "id": "evt_test_failed_001",
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_test_001",
                "amount": 50000,
                "currency": "inr",
                "payment_method_types": ["card"],
                "status": "requires_payment_method",
                "last_payment_error": {
                    "code": "card_declined",
                    "decline_code": "generic_decline",
                    "message": "Your card was declined.",
                },
                "created": 1788104210,
            }
        },
    }

    result = normalize_payment(payload)

    assert result["provider"] == "stripe"
    assert result["provider_payment_id"] == "pi_test_001"
    assert result["amount_minor"] == 50000
    assert result["currency"] == "INR"
    assert result["method"] == "card"
    assert result["status"] == "failed"
    assert result["error_code"] == "card_declined"
    assert result["error_source"] == "stripe"
    assert result["error_step"] == "payment_authorization"
    assert result["error_reason"] == "payment_failed"
