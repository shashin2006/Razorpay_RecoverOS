from app.services.razorpay_client import client


def create_recovery_payment_link(
    amount_minor: int,
    currency: str,
    description: str,
    recovery_case_id: int,
):
    payment_link = client.payment_link.create(
        {
            "amount": amount_minor,
            "currency": currency,
            "description": description,
            "reference_id": f"recovery_case_{recovery_case_id}",
            "reminder_enable": True,
        }
    )

    return payment_link