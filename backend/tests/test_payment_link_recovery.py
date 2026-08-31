from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import RecoveryAction, RecoveryCase
from app.services.event_processor import process_webhook_event


def test_payment_link_paid_recovers_case():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_link_completion_001",
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

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Bank declined original payment.",
        external_id="plink_test_completion_001",
        payment_link_url="https://rzp.io/test",
        created_at=datetime.now(timezone.utc),
        executed_at=datetime.now(timezone.utc),
    )

    db.add(action)
    db.commit()

    try:

        payload = {
            "event": "payment_link.paid",
            "entity": "event",
            "payload": {
                "payment_link": {
                    "entity": {
                        "id": "plink_test_completion_001",
                        "status": "paid",
                        "amount": 50000,
                        "amount_paid": 50000,
                        "currency": "INR",
                    }
                },
                "payment": {
                    "entity": {
                        "id": "pay_recovery_001",
                        "amount": 50000,
                        "currency": "INR",
                        "status": "captured",
                    }
                },
            },
        }

        process_webhook_event(
            db=db,
            event_type="payment_link.paid",
            payload=payload,
        )

        db.refresh(case)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000

    finally:

        db.delete(action)
        db.delete(case)
        db.commit()
        db.close()


def test_payment_link_paid_is_idempotent_for_recovery():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_link_completion_002",
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

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Bank declined original payment.",
        external_id="plink_test_completion_002",
        payment_link_url="https://rzp.io/test",
        created_at=datetime.now(timezone.utc),
        executed_at=datetime.now(timezone.utc),
    )

    db.add(action)
    db.commit()

    try:

        payload = {
            "event": "payment_link.paid",
            "entity": "event",
            "payload": {
                "payment_link": {
                    "entity": {
                        "id": "plink_test_completion_002",
                        "status": "paid",
                        "amount": 50000,
                        "amount_paid": 50000,
                        "currency": "INR",
                    }
                },
                "payment": {
                    "entity": {
                        "id": "pay_recovery_002",
                        "amount": 50000,
                        "currency": "INR",
                        "status": "captured",
                    }
                },
            },
        }

        # First webhook
        process_webhook_event(
            db=db,
            event_type="payment_link.paid",
            payload=payload,
        )

        db.refresh(case)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000

        # Duplicate webhook
        process_webhook_event(
            db=db,
            event_type="payment_link.paid",
            payload=payload,
        )

        db.refresh(case)

        # Must NOT become ₹1000.
        assert case.status == "recovered"
        assert case.amount_recovered == 50000

    finally:

        db.delete(action)
        db.delete(case)
        db.commit()
        db.close()