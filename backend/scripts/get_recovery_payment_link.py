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

payment_link_id = "plink_TWIwpD6da3KIWm"

payment_link = client.payment_link.fetch(
    payment_link_id
)

print("Payment Link:")
print("ID:", payment_link["id"])
print("Status:", payment_link["status"])
print("Amount:", payment_link["amount"])
print("Currency:", payment_link["currency"])
print("Short URL:", payment_link["short_url"])