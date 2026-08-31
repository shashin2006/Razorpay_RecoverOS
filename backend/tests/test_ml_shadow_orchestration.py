from datetime import datetime, timezone
from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
    Payment,
    RecoveryAction,
    RecoveryCase,
)
from app.services.recovery_orchestrator import (
    orchestrate_payment_failure,
)


@patch(
    "app.services.recovery_orchestrator.evaluate_ml_against_policy"
)
@patch(
    "app.services.recovery_orchestrator.execute_recovery_action"
)
def test_payment_failure_records_ml_shadow_prediction(
    mock_execute,
    mock_ml_decision,
):

    db = SessionLocal()

    payment_id = (
        "pay_ml_shadow_test_001"
    )

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id=(
            "order_ml_shadow_test_001"
        ),
        amount_minor=50000,
        currency="INR",
        method="netbanking",
        status="failed",
        error_code="BAD_REQUEST_ERROR",
        error_step="payment_authorization",
        error_reason="payment_failed",
        error_source="bank",
        error_description=(
            "Bank declined payment."
        ),
        created_at=datetime.now(
            timezone.utc
        ),
        updated_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    recovery_case = None

    try:

        recovery_case = RecoveryCase(
            payment_id=payment_id,
            amount_at_risk_minor=50000,
            amount_recovered=0,
            currency="INR",
            failure_category="bank_decline",
            status="open",
            attempts=0,
        )

        db.add(recovery_case)
        db.commit()
        db.refresh(recovery_case)

        mock_execute.return_value.status = (
            type(
                "Status",
                (),
                {"value": "created"},
            )()
        )

        mock_execute.return_value.action = (
            "alternate_payment_method"
        )

        mock_execute.return_value.external_id = (
            "plink_shadow_test_001"
        )

        mock_execute.return_value.payment_link_url = (
            "https://rzp.io/test"
        )

        mock_execute.return_value.message = (
            "Recovery payment link created."
        )

        mock_ml_decision.return_value = (
            type(
                "MLDecision",
                (),
                {
                    "policy_eligible": True,
                    "policy_action": (
                        "alternate_payment_method"
                    ),
                    "ml_probability": 0.69,
                    "ml_recommendation": True,
                    "threshold": 0.40,
                    "agreement": True,
                },
            )()
        )

        result = orchestrate_payment_failure(
            db=db,
            payment=payment,
            payment_data={
                "error_source": "bank",
                "error_step": (
                    "payment_authorization"
                ),
                "error_reason": "payment_failed",
                "error_code": "BAD_REQUEST_ERROR",
            },
        )

        assert result["status"] == "created"

        mock_ml_decision.assert_called_once()

        call_kwargs = (
            mock_ml_decision.call_args.kwargs
        )

        assert call_kwargs["payment"] is payment
        assert (
            call_kwargs["recovery_case"]
            is recovery_case
        )

    finally:

        db.query(MLPrediction).filter(
            MLPrediction.recovery_case_id
            == recovery_case.id
        ).delete(
            synchronize_session=False
        )

        db.query(MLDecisionAudit).filter(
            MLDecisionAudit.recovery_case_id
            == recovery_case.id
        ).delete(
            synchronize_session=False
        )

        db.query(RecoveryAction).filter(
            RecoveryAction.recovery_case_id
            == recovery_case.id
        ).delete(
            synchronize_session=False
        )

        db.delete(recovery_case)
        db.delete(payment)

        db.commit()
        db.close()