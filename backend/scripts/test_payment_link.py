from app.services.payment_link import create_recovery_payment_link

# Replace with an existing open RecoveryCase ID when running manually.
RECOVERY_CASE_ID = 1

payment_link = create_recovery_payment_link(
    amount_minor=50000,
    currency="INR",
    description="RecoveryOS Test Recovery",
    recovery_case_id=RECOVERY_CASE_ID,
)

print("Stripe Checkout Session:")
print(payment_link)
