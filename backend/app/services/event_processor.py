from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Payment, RecoveryAction, RecoveryCase
from app.services.payment_normalizer import normalize_payment
from app.services.payment_state import is_valid_transition
from app.services.recovery_completion import mark_recovery_recovered
from app.services.recovery_orchestrator import (
    orchestrate_payment_failure,
)
from app.services.ml_outcome_service import (
    record_recovery_outcome,
)


PAYMENT_EVENTS = {
    "payment.authorized",
    "payment.failed",
    "payment.captured",
}

RECOVERY_EVENTS = {
    "payment_link.paid",
}


def process_payment_recovery(
    db: Session,
    payload: dict[str, Any],
) -> None:

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if not payment:
        return

    notes = payment.get("notes") or {}

    recovery_case_id = notes.get("recovery_case_id")

    if not recovery_case_id:
        return

    try:
        recovery_case_id = int(recovery_case_id)
    except (TypeError, ValueError):
        return

    recovery_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.id == recovery_case_id
        )
        .first()
    )

    if recovery_case is None:
        return

    amount_recovered = payment.get("amount")

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


def process_payment_link_paid(
    db: Session,
    payload: dict[str, Any],
) -> None:

    payment_link = (
        payload
        .get("payload", {})
        .get("payment_link", {})
        .get("entity", {})
    )

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    payment_link_id = payment_link.get("id")
    payment_id = payment.get("id")
    amount_paid = payment.get("amount")

    if not payment_link_id:
        return

    if not payment_id:
        return

    if amount_paid is None:
        return

    action = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.external_id == payment_link_id
        )
        .first()
    )

    if action is None:
        return

    recovery_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.id == action.recovery_case_id
        )
        .first()
    )

    if recovery_case is None:
        return

    if recovery_case.status == "recovered":
        return

    mark_recovery_recovered(
        db=db,
        recovery_case=recovery_case,
        amount_recovered=amount_paid,
    )
    record_recovery_outcome(
        db=db,
        recovery_case_id=recovery_case.id,
        amount_recovered=amount_paid,
    )


def process_webhook_event(
    db: Session,
    event_type: str,
    payload: dict[str, Any],
) -> None:

    # --------------------------------------------------
    # PAYMENT LINK RECOVERY EVENT
    # --------------------------------------------------

    if event_type in RECOVERY_EVENTS:

        if event_type == "payment_link.paid":
            process_payment_link_paid(
                db=db,
                payload=payload,
            )

        return

    # --------------------------------------------------
    # PAYMENT EVENTS
    # --------------------------------------------------

    if event_type not in PAYMENT_EVENTS:
        return

    normalized = normalize_payment(payload)

    now = datetime.now(timezone.utc)

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_payment_id
            == normalized["razorpay_payment_id"]
        )
        .first()
    )

    # --------------------------------------------------
    # NEW PAYMENT
    # --------------------------------------------------

    if existing_payment is None:

        payment = Payment(
            **normalized,
            updated_at=now,
        )

        db.add(payment)
        db.commit()

        if event_type == "payment.failed":
            payment_data = {
                "error_source": normalized["error_source"],
                "error_step": normalized["error_step"],
                "error_reason": normalized["error_reason"],
                "error_code": normalized["error_code"],
            }

            orchestrate_payment_failure(
                db=db,
                payment=payment,
                payment_data=payment_data,
            )
        
        if event_type == "payment.captured":
            process_payment_recovery(
                db=db,
                payload=payload,
            )

        return

    # --------------------------------------------------
    # EXISTING PAYMENT
    # --------------------------------------------------

    current_status = existing_payment.status
    new_status = normalized["status"]

    if not is_valid_transition(
        current_status,
        new_status,
    ):
        return

    # --------------------------------------------------
    # VALID STATE TRANSITION
    # --------------------------------------------------

    for key, value in normalized.items():

        if key == "created_at":
            continue

        setattr(
            existing_payment,
            key,
            value,
        )

    existing_payment.updated_at = now

    db.commit()

    # --------------------------------------------------
    # RECOVERY COMPLETION
    # --------------------------------------------------

    if event_type == "payment.captured":
        process_payment_recovery(
            db=db,
            payload=payload,
        )