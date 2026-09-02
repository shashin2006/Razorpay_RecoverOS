from datetime import datetime, timezone
from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
from app.services.llm.agent_tools import (
    execute_bounded_recovery,
)


def test_bounded_recovery_allows_policy_action():

    db = SessionLocal()

    payment_id = "pay_agent_test_001"

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id="order_agent_test_001",
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

    case = RecoveryCase(
        payment_id=payment_id,
        amount_at_risk_minor=50000,
        amount_recovered=0,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=0,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    try:

        mock_result = type(
            "Result",
            (),
            {
                "status": type(
                    "Status",
                    (),
                    {"value": "created"},
                )(),
                "action": "alternate_payment_method",
                "external_id": "agent_test_link",
                "payment_link_url": "https://rzp.io/test",
                "message": "Recovery link created.",
            },
        )()

        with patch(
            "app.services.llm.agent_tools.execute_recovery_action",
            return_value=mock_result,
        ) as mock_execute:

            result = execute_bounded_recovery(
                db=db,
                recovery_case_id=case.id,
                action="alternate_payment_method",
            )

        assert result["executed"] is True

        mock_execute.assert_called_once()

    finally:

        db.delete(case)
        db.delete(payment)
        db.commit()
        db.close()