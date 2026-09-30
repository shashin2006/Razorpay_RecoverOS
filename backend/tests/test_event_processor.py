from app.db.models import Payment
from app.services.event_processor import process_webhook_event


def test_process_failed_stripe_payment(db_session):
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

    process_webhook_event(
        db=db_session,
        event_type="payment_intent.payment_failed",
        payload=payload,
    )

    payment = (
        db_session.query(Payment)
        .filter(Payment.provider_payment_id == "pi_test_001")
        .first()
    )

    assert payment is not None
    assert payment.provider == "stripe"
    assert payment.amount_minor == 50000
    assert payment.currency == "INR"
    assert payment.status == "failed"
    assert payment.method == "card"
    assert payment.error_source == "stripe"
    assert payment.error_step == "payment_authorization"
    assert payment.error_reason == "payment_failed"
