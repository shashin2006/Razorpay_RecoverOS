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
        "receipt": "recoveryos_test_002",
    }
)


print("Order created:")
print(order)