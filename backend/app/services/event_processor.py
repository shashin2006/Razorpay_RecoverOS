from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Payment
from app.services.payment_normalizer import normalize_payment
from app.services.payment_state import is_valid_transition


PAYMENT_EVENTS = {
    "payment.authorized",
    "payment.failed",
    "payment.captured",
}


def process_webhook_event(
    db: Session,
    event_type: str,
    payload: dict[str, Any],
) -> None:

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