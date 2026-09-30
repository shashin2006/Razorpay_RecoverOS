import stripe
from app.core.config import settings

stripe.api_key = settings.stripe_secret_key

payment_intent = stripe.PaymentIntent.create(
    amount=50000,
    currency="inr",
    payment_method="pm_card_chargeDeclined",
    confirm=True,
    metadata={"recoveryos_test": "true"},
)

print("Stripe PaymentIntent:")
print("ID:", payment_intent.id)
print("Status:", payment_intent.status)
print("Amount:", payment_intent.amount)
print("Currency:", payment_intent.currency)
