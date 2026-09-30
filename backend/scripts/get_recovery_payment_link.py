import stripe

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key

CHECKOUT_SESSION_ID = "cs_test_replace_me"

session = stripe.checkout.Session.retrieve(CHECKOUT_SESSION_ID)

print("Stripe Checkout Session:")
print("ID:", session.id)
print("Status:", session.status)
print("Payment Status:", session.payment_status)
print("Amount:", session.amount_total)
print("Currency:", session.currency)
print("URL:", session.url)
