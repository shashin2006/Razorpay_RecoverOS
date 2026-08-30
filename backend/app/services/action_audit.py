from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import RecoveryAction


def record_action(
    db: Session,
    recovery_case_id: int,
    action_type: str,
    status: str,
    attempt_number: int,
    reason: str,
    external_id: str | None = None,
) -> RecoveryAction:

    action = RecoveryAction(
        recovery_case_id=recovery_case_id,
        action_type=action_type,
        status=status,
        attempt_number=attempt_number,
        reason=reason,
        external_id=external_id,
        created_at=datetime.now(timezone.utc),
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action