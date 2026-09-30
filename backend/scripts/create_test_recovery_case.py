from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.db.models import Payment
from app.services.recovery_case import create_recovery_case
from app.services.failure_classifier import classify_failure


db = SessionLocal()

try:
    payment_id = "pay_e2e_agent_001"

    # ----------------------------------------
    # Check whether test payment already exists
    # ----------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.razorpay_payment_id == payment_id)
        .first()
    )

    if payment is None:
        now = datetime.now(timezone.utc)

        payment = Payment(
            razorpay_payment_id=payment_id,
            razorpay_order_id="order_e2e_test_001",
            amount_minor=50000,
            currency="INR",
            method="netbanking",
            status="failed",
            error_code="BAD_REQUEST_ERROR",
            error_step="payment_authorization",
            error_reason="payment_failed",
            error_source="bank",
            error_description="Bank authorization declined the payment.",
            created_at=now,
            updated_at=now,
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        print("Payment created.")
    else:
        print("Payment already exists.")

    # ----------------------------------------
    # Classify payment failure
    # ----------------------------------------

    payment_data = {
        "error_code": payment.error_code,
        "error_source": payment.error_source,
        "error_step": payment.error_step,
        "error_reason": payment.error_reason,
        "error_description": payment.error_description,
    }

    classification = classify_failure(payment_data)

    # ----------------------------------------
    # Create RecoveryCase using service
    # ----------------------------------------

    recovery_case = create_recovery_case(
        db=db,
        payment_id=payment.razorpay_payment_id,
        amount_at_risk_minor=payment.amount_minor,
        currency=payment.currency,
        classification=classification,
    )

    print()
    print("Recovery Case ready:")
    print("ID:", recovery_case.id)
    print("Payment ID:", recovery_case.payment_id)
    print("Amount at risk:", recovery_case.amount_at_risk_minor)
    print("Currency:", recovery_case.currency)
    print("Failure category:", recovery_case.failure_category)
    print("Status:", recovery_case.status)
    print("Attempts:", recovery_case.attempts)

finally:
    db.close()