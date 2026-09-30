from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import RecoveryCase

from app.services.recovery_completion import (
    mark_recovery_recovered,
)


def test_open_case_becomes_recovered():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_completion_test_001",
        amount_at_risk_minor=50000,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        amount_recovered=0,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    try:

        result = mark_recovery_recovered(
            db=db,
            recovery_case=case,
            amount_recovered=50000,
        )

        assert result.status == "recovered"
        assert result.amount_recovered == 50000

    finally:

        db.delete(case)
        db.commit()
        db.close()


def test_recovered_case_does_not_change():

    db = SessionLocal()

    case = RecoveryCase(
        payment_id="pay_completion_test_002",
        amount_at_risk_minor=50000,
        currency="INR",
        failure_category="bank_decline",
        status="recovered",
        attempts=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        amount_recovered=50000,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    try:

        result = mark_recovery_recovered(
            db=db,
            recovery_case=case,
            amount_recovered=25000,
        )

        assert result.status == "recovered"

        # Existing recovered amount must not be overwritten.
        assert result.amount_recovered == 50000

    finally:

        db.delete(case)
        db.commit()
        db.close()