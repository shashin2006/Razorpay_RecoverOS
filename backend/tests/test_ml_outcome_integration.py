from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import MLPrediction, RecoveryCase
from app.services.event_processor import (
    process_payment_link_paid,
)


def test_payment_link_paid_records_ml_outcome():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_ml_outcome_integration_001",
        amount_at_risk_minor=50000,
        amount_recovered=0,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=1,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    prediction = MLPrediction(
        recovery_case_id=case.id,
        probability=0.6916,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        actual_recovered=None,
        outcome_recorded=False,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    try:

        from app.db.models import RecoveryAction

        action = RecoveryAction(
            recovery_case_id=case.id,
            action_type="alternate_payment_method",
            status="executed",
            attempt_number=1,
            reason="Bank declined payment.",
            external_id="plink_ml_outcome_test_001",
        )

        db.add(action)
        db.commit()

        payload = {
            "payload": {
                "payment_link": {
                    "entity": {
                        "id": "plink_ml_outcome_test_001",
                    }
                },
                "payment": {
                    "entity": {
                        "id": "pay_recovery_success_001",
                        "amount": 50000,
                    }
                },
            }
        }

        process_payment_link_paid(
            db=db,
            payload=payload,
        )

        db.refresh(prediction)

        assert prediction.actual_recovered == 50000
        assert prediction.outcome_recorded is True

        db.refresh(case)

        assert case.status == "recovered"
        assert case.amount_recovered == 50000

    finally:

        db.delete(prediction)

        db.query(RecoveryAction).filter(
            RecoveryAction.recovery_case_id == case.id
        ).delete(
            synchronize_session=False
        )

        db.delete(case)

        db.commit()
        db.close()