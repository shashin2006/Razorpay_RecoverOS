from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import MLPrediction, RecoveryAction, RecoveryCase
from app.services.event_processor import process_webhook_event


def make_case(db, case_id: str):
    case = RecoveryCase(
        payment_id=case_id,
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
    return case


def test_checkout_session_completed_recovers_case():
    db = SessionLocal()
    case = make_case(db, "pi_original_001")

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Payment declined during authorization.",
        external_id="cs_test_completion_001",
        payment_link_url="https://checkout.stripe.com/test",
        created_at=datetime.now(timezone.utc),
        executed_at=datetime.now(timezone.utc),
    )
    db.add(action)
    db.commit()

    try:
        payload = {
            "id": "evt_checkout_001",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_completion_001",
                    "amount_total": 50000,
                    "currency": "inr",
                    "metadata": {"recovery_case_id": str(case.id)},
                    "payment_status": "paid",
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="checkout.session.completed",
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


def test_checkout_session_completed_is_idempotent():
    db = SessionLocal()
    case = make_case(db, "pi_original_002")

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Payment declined during authorization.",
        external_id="cs_test_completion_002",
        payment_link_url="https://checkout.stripe.com/test",
        created_at=datetime.now(timezone.utc),
        executed_at=datetime.now(timezone.utc),
    )
    db.add(action)
    db.commit()

    payload = {
        "id": "evt_checkout_002",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_completion_002",
                "amount_total": 50000,
                "currency": "inr",
                "metadata": {"recovery_case_id": str(case.id)},
                "payment_status": "paid",
            }
        },
    }

    try:
        process_webhook_event(db=db, event_type="checkout.session.completed", payload=payload)
        process_webhook_event(db=db, event_type="checkout.session.completed", payload=payload)
        db.refresh(case)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000
    finally:
        db.delete(action)
        db.delete(case)
        db.commit()
        db.close()


def test_checkout_session_completed_records_ml_outcome():
    db = SessionLocal()
    case = make_case(db, "pi_original_003")

    prediction = MLPrediction(
        recovery_case_id=case.id,
        probability=0.7491,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
    )
    db.add(prediction)

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Payment declined during authorization.",
        external_id="cs_test_ml_001",
        payment_link_url="https://checkout.stripe.com/test",
        created_at=datetime.now(timezone.utc),
        executed_at=datetime.now(timezone.utc),
    )
    db.add(action)
    db.commit()

    try:
        payload = {
            "id": "evt_checkout_ml_001",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_ml_001",
                    "amount_total": 50000,
                    "currency": "inr",
                    "metadata": {"recovery_case_id": str(case.id)},
                    "payment_status": "paid",
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="checkout.session.completed",
            payload=payload,
        )

        db.refresh(case)
        db.refresh(prediction)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000
        assert prediction.actual_recovered == 50000
        assert prediction.outcome_recorded is True
    finally:
        db.delete(prediction)
        db.delete(action)
        db.delete(case)
        db.commit()
        db.close()
