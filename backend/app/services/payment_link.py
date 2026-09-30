import stripe

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key


def create_recovery_payment_link(
    amount_minor: int,
    currency: str,
    description: str,
    recovery_case_id: int,
):
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {"name": description},
                    "unit_amount": amount_minor,
                },
                "quantity": 1,
            }
        ],
        metadata={
            "recovery_case_id": str(recovery_case_id),
            "recoveryos": "true",
        },
        success_url=(
            "http://localhost:3000/recovery/success"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url="http://localhost:3000/?recovery=cancel",
    )

    return {
        "id": session.id,
        "short_url": session.url,
    }
