from app.db.database import SessionLocal
from app.db.models import RecoveryAction

from app.services.action_audit import record_action


def test_record_recovery_action():

    db = SessionLocal()

    try:

        action = record_action(
            db=db,
            recovery_case_id=999999,
            action_type="alternate_payment_method",
            status="created",
            attempt_number=1,
            reason="Bank authorization decline.",
        )

        assert action.id is not None
        assert action.recovery_case_id == 999999
        assert action.action_type == "alternate_payment_method"
        assert action.status == "created"
        assert action.attempt_number == 1
        assert action.external_id is None

    finally:

        db.query(RecoveryAction).filter(
            RecoveryAction.id == action.id
        ).delete()

        db.commit()
        db.close()

def test_record_executed_action():

    db = SessionLocal()

    try:

        action = record_action(
            db=db,
            recovery_case_id=999998,
            action_type="alternate_payment_method",
            status="executed",
            attempt_number=1,
            reason="Bank authorization decline.",
            external_id="plink_test_001",
        )

        assert action.status == "executed"
        assert action.external_id == "plink_test_001"

    finally:

        db.query(RecoveryAction).filter(
            RecoveryAction.id == action.id
        ).delete()

        db.commit()
        db.close()