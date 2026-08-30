from app.db.models import Payment
from app.services.event_processor import process_webhook_event


def test_process_failed_payment(db_session):

    payload = {
        "event": "payment.failed",
        "entity": "event",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_processor_test_001",
                    "amount": 50000,
                    "currency": "INR",
                    "method": "netbanking",
                    "status": "failed",
                    "order_id": "order_processor_test_001",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_step": "payment_authorization",
                    "error_reason": "payment_failed",
                    "error_source": "bank",
                    "error_description": "Bank declined payment.",
                }
            }
        },
    }

    process_webhook_event(
        db=db_session,
        event_type="payment.failed",
        payload=payload,
    )

    payment = (
        db_session.query(Payment)
        .filter(
            Payment.razorpay_payment_id
            == "pay_processor_test_001"
        )
        .first()
    )

    assert payment is not None
    assert payment.amount_minor == 50000
    assert payment.currency == "INR"
    assert payment.status == "failed"
    assert payment.method == "netbanking"
    assert payment.error_source == "bank"
    assert payment.error_step == "payment_authorization"