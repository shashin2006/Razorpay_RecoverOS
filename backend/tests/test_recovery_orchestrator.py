from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
from app.services.recovery_orchestrator import (
    orchestrate_payment_failure,
)
from unittest.mock import patch

@patch(
    "app.services.recovery_orchestrator.execute_recovery_action"
)
def test_bank_decline_creates_recovery_case(
    mock_execute,
):

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

        mock_execute.return_value = type(
            "Result",
            (),
            {
                "status": type(
                    "Status",
                    (),
                    {"value": "created"},
                )(),
                "action": "alternate_payment_method",
                "external_id": "plink_test_001",
                "payment_link_url": "https://rzp.io/test",
                "message": "Recovery payment link created.",
            },
        )()

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

        mock_execute.assert_called_once()

    finally:

        db.query(
            RecoveryCase
        ).filter(
            RecoveryCase.payment_id == payment_id
        ).delete(
            synchronize_session=False
        )

        db.delete(payment)

        db.commit()
        db.close()