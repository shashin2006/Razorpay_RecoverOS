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

    if amount_recovered <= 0:
        return recovery_case

    # Never record more recovered revenue than was at risk.
    recovered_amount = min(
        amount_recovered,
        recovery_case.amount_at_risk_minor,
    )

    recovery_case.amount_recovered = (
        recovered_amount
    )

    recovery_case.status = "recovered"

    recovery_case.updated_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(recovery_case)

    return recovery_case