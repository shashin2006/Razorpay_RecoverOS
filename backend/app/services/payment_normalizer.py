from typing import Any
from datetime import datetime, timezone


def normalize_payment(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a Razorpay webhook payload into
    our internal Payment representation.
    """

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if not payment:
        raise ValueError(
            "Payment entity missing from Razorpay payload"
        )

    payment_id = payment.get("id")

    if not payment_id:
        raise ValueError(
            "Razorpay payment ID missing"
        )
    
    razorpay_created_at = payment.get("created_at")

    if razorpay_created_at is None:
        created_at = datetime.now(timezone.utc)
    else:
        created_at = datetime.fromtimestamp(
            razorpay_created_at,
            tz=timezone.utc,
        )


    return {
        "razorpay_payment_id": payment_id,
        "razorpay_order_id": payment.get("order_id"),
        "amount_minor": payment.get("amount"),
        "currency": payment.get("currency"),
        "method": payment.get("method"),
        "status": payment.get("status"),
        "error_code": payment.get("error_code"),
        "error_step": payment.get("error_step"),
        "error_reason": payment.get("error_reason"),
        "error_source": payment.get("error_source"),
        "error_description": payment.get(
            "error_description"
        ),
        "created_at": created_at,
    }