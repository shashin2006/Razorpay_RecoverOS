from typing import Any
from datetime import datetime, timezone


def normalize_payment(
    payload: dict[str, Any]
) -> dict[str, Any]:

    intent = payload.get("data", {}).get("object", {})

    if not intent:
        raise ValueError(
            "PaymentIntent missing from Stripe payload"
        )

    payment_id = intent.get("id")

    if not payment_id:
        raise ValueError(
            "Stripe PaymentIntent ID missing"
        )

    created_timestamp = intent.get("created")

    created_at = (
        datetime.fromtimestamp(
            created_timestamp,
            tz=timezone.utc,
        )
        if created_timestamp
        else datetime.now(timezone.utc)
    )

    last_error = intent.get("last_payment_error") or {}

    return {
        "provider": "stripe",

        "provider_payment_id": payment_id,

        "provider_order_id": (
            intent.get("metadata", {})
            .get("recoveryos_order_id")
        ),

        "amount_minor": intent.get("amount", 0),

        "currency": (
            intent.get("currency") or ""
        ).upper(),

        "method": (
            intent.get("payment_method_types", ["card"])[0]
            if intent.get("payment_method_types")
            else "card"
        ),

        "status": intent.get("status"),

        "error_code": last_error.get("code"),

        "error_step": "payment",

        "error_reason": (
            last_error.get("decline_code")
            or last_error.get("code")
        ),

        "error_source": "stripe",

        "error_description": last_error.get(
            "message"
        ),

        "created_at": created_at,
    }