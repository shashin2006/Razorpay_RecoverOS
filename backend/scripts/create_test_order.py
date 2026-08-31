import os

import razorpay
from dotenv import load_dotenv


load_dotenv()

client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET"),
    )
)

order = client.order.create(
    {
        "amount": 50000,
        "currency": "INR",
        "receipt": "recoveryos_auto_test_003",
    }
)

print("Order created:")
print("Order ID:", order["id"])
print("Amount:", order["amount"])
print("Currency:", order["currency"])
print("Receipt:", order["receipt"])