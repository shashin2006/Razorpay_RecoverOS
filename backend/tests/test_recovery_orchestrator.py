from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
from app.services.recovery_orchestrator import (
    orchestrate_payment_failure,
)



def test_bank_decline_creates_recovery_case():

    db = SessionLocal()

    payment_id = "pay_orchestrator_test_001"

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id="order_orchestrator_test_001",
        amount_minor=50000,
        currency="INR",
        method="netbanking",
        status="failed",
        error_code="BAD_REQUEST_ERROR",
        error_step="payment_authorization",
        error_reason="payment_failed",
        error_source="bank",
        error_description="Bank declined payment.",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:

        payment_data = {
            "error_source": "bank",
            "error_step": "payment_authorization",
            "error_reason": "payment_failed",
            "error_code": "BAD_REQUEST_ERROR",
        }

        result = orchestrate_payment_failure(
            db=db,
            payment=payment,
            payment_data=payment_data,
        )

        assert result["status"] == "created"
        assert result["category"] == "bank_decline"
        assert result["action"] == "alternate_payment_method"

        case = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id == payment_id
            )
            .first()
        )

        assert case is not None
        assert case.status == "open"
        assert case.attempts == 1
        assert case.amount_at_risk_minor == 50000

    finally:

        case = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id == payment_id
            )
            .first()
        )

        if case:
            db.delete(case)

        db.delete(payment)
        db.commit()
        db.close()