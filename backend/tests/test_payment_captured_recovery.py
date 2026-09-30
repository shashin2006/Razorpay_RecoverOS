from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import RecoveryCase
from app.services.event_processor import process_webhook_event


def test_payment_captured_recovers_case_from_notes():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_recovery_notes_001",
        amount_at_risk_minor=50000,
        amount_recovered=0,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    try:

        payload = {
            "event": "payment.captured",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_TWHomYuKVbD6xC",
                        "order_id": "order_TWHnKH8RJcP0Hy",
                        "amount": 50000,
                        "currency": "INR",
                        "method": "netbanking",
                        "status": "captured",
                        "captured": True,
                        "notes": {
                            "recovery_case_id": str(case.id)
                        },
                        "created_at": 1788159545,
                        "error_code": None,
                        "error_step": None,
                        "error_reason": None,
                        "error_source": None,
                        "error_description": None,
                    }
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="payment.captured",
            payload=payload,
        )

        db.refresh(case)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000

    finally:

        db.delete(case)
        db.commit()
        db.close()