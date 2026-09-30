from app.services.payment_link import (
    create_recovery_payment_link,
)


payment_link = create_recovery_payment_link(
    amount_minor=50000,
    currency="INR",
    description="RecoveryOS Test Recovery",
)

print("Payment Link created:")
print(payment_link)