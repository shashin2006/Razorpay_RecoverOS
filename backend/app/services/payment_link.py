from app.services.razorpay_client import client


def create_recovery_payment_link(
    amount_minor: int,
    currency: str,
    description: str,
    recovery_case_id: int,
):

    reference_id = f"recovery_case_{recovery_case_id}"

    payment_link = client.payment_link.create(
        {
            "amount": amount_minor,
            "currency": currency,
            "description": description,
            "reference_id": reference_id,
            "notes": {
                "recovery_case_id": str(recovery_case_id),
            },
            "reminder_enable": True,
        }
    )

    print("DEBUG PAYMENT LINK RESPONSE:")
    print(payment_link)

    return payment_link