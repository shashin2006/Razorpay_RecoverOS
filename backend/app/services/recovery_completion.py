from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import RecoveryCase


def mark_recovery_recovered(
    db: Session,
    recovery_case: RecoveryCase,
    amount_recovered: int,
):
    # Never reopen or modify an already completed case.
    if recovery_case.status == "recovered":
        return recovery_case

    recovery_case.amount_recovered = amount_recovered
    recovery_case.status = "recovered"
    recovery_case.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(recovery_case)

    return recovery_case