from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import RecoveryCase
from app.services.failure_classifier import (
    FailureClassification,
)


def create_recovery_case(
    db: Session,
    payment_id: str,
    amount_at_risk_minor: int,
    currency: str,
    classification: FailureClassification,
) -> RecoveryCase:

    existing_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.payment_id == payment_id
        )
        .first()
    )

    if existing_case:
        return existing_case

    now = datetime.now(timezone.utc)

    recovery_case = RecoveryCase(
        payment_id=payment_id,
        amount_at_risk_minor=amount_at_risk_minor,
        currency=currency,
        failure_category=classification.category.value,
        status="open",
        attempts=0,
        created_at=now,
        updated_at=now,
    )

    db.add(recovery_case)
    db.commit()
    db.refresh(recovery_case)

    return recovery_case