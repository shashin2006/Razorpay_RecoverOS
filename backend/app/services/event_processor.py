from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Payment, RecoveryCase
from app.services.ml_outcome_service import record_recovery_outcome
from app.services.payment_normalizer import normalize_payment
from app.services.payment_state import is_valid_transition
from app.services.recovery_completion import mark_recovery_recovered
from app.services.recovery_orchestrator import orchestrate_payment_failure


PAYMENT_EVENTS = {"payment_intent.payment_failed", "payment_intent.succeeded"}
RECOVERY_EVENTS = {"checkout.session.completed"}


def process_recovery_checkout(db: Session, payload: dict[str, Any]) -> None:
    session = payload.get("data", {}).get("object", {})
    recovery_case_id = (session.get("metadata") or {}).get("recovery_case_id")
    if not recovery_case_id:
        return

    try:
        recovery_case_id = int(recovery_case_id)
    except (TypeError, ValueError):
        return

    recovery_case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == recovery_case_id)
        .first()
    )
    if recovery_case is None or recovery_case.status == "recovered":
        return

    amount_recovered = session.get("amount_total")
    if amount_recovered is None:
        return

    mark_recovery_recovered(
        db=db,
        recovery_case=recovery_case,
        amount_recovered=amount_recovered,
    )
    record_recovery_outcome(
        db=db,
        recovery_case_id=recovery_case.id,
        amount_recovered=amount_recovered,
    )


def process_webhook_event(
    db: Session,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    if event_type in RECOVERY_EVENTS:
        process_recovery_checkout(db=db, payload=payload)
        return

    if event_type not in PAYMENT_EVENTS:
        return

    normalized = normalize_payment(payload)
    now = datetime.now(timezone.utc)

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.provider_payment_id
            == normalized["provider_payment_id"]
        )
        .first()
    )

    if existing_payment is None:
        payment = Payment(
            **normalized,
            updated_at=now,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        if event_type == "payment_intent.payment_failed":
            orchestrate_payment_failure(
                db=db,
                payment=payment,
                payment_data={
                    "error_source": normalized["error_source"],
                    "error_step": normalized["error_step"],
                    "error_reason": normalized["error_reason"],
                    "error_code": normalized["error_code"],
                },
            )
        return

    current_status = existing_payment.status
    new_status = normalized["status"]

    if not is_valid_transition(current_status, new_status):
        return

    for key, value in normalized.items():
        if key != "created_at":
            setattr(existing_payment, key, value)

    existing_payment.updated_at = now
    db.commit()
