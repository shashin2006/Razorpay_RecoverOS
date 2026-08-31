from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
from app.services.action_executor import (
    ActionExecutionResult,
    ActionExecutionStatus,
)
from app.services.event_processor import process_webhook_event


@patch(
    "app.services.recovery_orchestrator.execute_recovery_action"
)
def test_payment_failed_automatically_creates_recovery(
    mock_execute_action,
):

    mock_execute_action.return_value = ActionExecutionResult(
        status=ActionExecutionStatus.CREATED,
        action="alternate_payment_method",
        external_id="plink_automatic_test_001",
        payment_link_url="https://rzp.io/test",
        message="Recovery payment link created.",
    )

    db = SessionLocal()

    payment_id = "pay_automatic_recovery_test_001"

    try:

        payload = {
            "event": "payment.failed",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": payment_id,
                        "order_id": "order_automatic_test_001",
                        "amount": 50000,
                        "currency": "INR",
                        "method": "netbanking",
                        "status": "failed",
                        "created_at": 1788104210,
                        "error_code": "BAD_REQUEST_ERROR",
                        "error_step": "payment_authorization",
                        "error_reason": "payment_failed",
                        "error_source": "bank",
                        "error_description": "Bank declined payment.",
                    }
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="payment.failed",
            payload=payload,
        )

        # ----------------------------------------
        # Payment was created
        # ----------------------------------------

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == payment_id
            )
            .first()
        )

        assert payment is not None
        assert payment.status == "failed"

        # ----------------------------------------
        # Recovery case was created
        # ----------------------------------------

        case = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id == payment_id
            )
            .first()
        )

        assert case is not None
        assert case.status == "open"
        assert case.amount_at_risk_minor == 50000
        assert case.failure_category == "bank_decline"

        # ----------------------------------------
        # Orchestrator selected the action
        # ----------------------------------------

        mock_execute_action.assert_called_once()

        call_kwargs = mock_execute_action.call_args.kwargs

        assert call_kwargs["action"] == "alternate_payment_method"
        assert call_kwargs["max_attempts"] == 3

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

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == payment_id
            )
            .first()
        )

        if payment:
            db.delete(payment)

        db.commit()
        db.close()