from datetime import datetime, timezone
from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import (
    Payment,
    RecoveryAction,
    RecoveryCase,
)
from app.services.llm.recovery_agent import (
    run_recovery_agent,
)


def _tool_call(
    call_id,
    name,
    arguments,
):
    return type(
        "ToolCall",
        (),
        {
            "id": call_id,
            "function": type(
                "Function",
                (),
                {
                    "name": name,
                    "arguments": arguments,
                },
            )(),
        },
    )()


def _response(
    content=None,
    tool_calls=None,
):
    return type(
        "Response",
        (),
        {
            "choices": [
                type(
                    "Choice",
                    (),
                    {
                        "message": type(
                            "Message",
                            (),
                            {
                                "content": content,
                                "tool_calls": tool_calls,
                            },
                        )()
                    },
                )()
            ]
        },
    )()


def test_agent_inspects_then_executes():

    db = SessionLocal()

    payment_id = (
        "pay_agent_tools_test_001"
    )

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id=(
            "order_agent_tools_test_001"
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

    try:

        inspect_call = _tool_call(
            "call_1",
            "inspect_recovery_case",
            (
                '{"recovery_case_id": '
                f'{recovery_case.id}'
                '}'
            ),
        )

        execute_call = _tool_call(
            "call_2",
            "execute_bounded_recovery",
            (
                '{"recovery_case_id": '
                f'{recovery_case.id}, '
                '"action": '
                '"alternate_payment_method"}'
            ),
        )

        responses = [
            _response(
                tool_calls=[inspect_call]
            ),
            _response(
                tool_calls=[execute_call]
            ),
            _response(
                content=(
                    "Recovery action completed "
                    "through the approved policy."
                )
            ),
        ]

        with patch(
            "app.services.llm.recovery_agent.client.chat.completions.create",
            side_effect=responses,
        ):

            # Mock the separate NVIDIA content-safety call.
            # The real recovery agent and recovery executor still run.
            with patch(
                "app.services.llm.recovery_agent.make_safe_customer_message"
            ) as mock_safety:

                mock_safety.return_value = {
                    "message": (
                        "Recovery action completed "
                        "through the approved policy."
                    ),
                    "safe": True,
                    "reason": "Test safety validation passed.",
                    "fallback_used": False,
                }

                # Mock ONLY the external Razorpay operation.
                with patch(
                    "app.services.action_executor.create_recovery_payment_link"
                ) as mock_payment_link:

                    mock_payment_link.return_value = {
                        "id": "plink_agent_test_001",
                        "short_url": "https://rzp.io/test",
                    }

                    result = run_recovery_agent(
                        db=db,
                        recovery_case_id=recovery_case.id,
                    )

        # ------------------------------------------------
        # AGENT COMPLETED
        # ------------------------------------------------

        assert result["status"] == "completed"

        # Agent should have inspected and then executed.
        assert len(
            result["tool_calls"]
        ) == 2

        assert (
            result["tool_calls"][0]["tool"]
            == "inspect_recovery_case"
        )

        assert (
            result["tool_calls"][1]["tool"]
            == "execute_bounded_recovery"
        )

        # External payment-link provider was called once.
        mock_payment_link.assert_called_once()

        # ------------------------------------------------
        # RECOVERY ACTION CREATED
        # ------------------------------------------------

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id
                == recovery_case.id
            )
            .first()
        )

        assert action is not None

        assert (
            action.action_type
            == "alternate_payment_method"
        )

        assert action.status == "executed"

        assert action.attempt_number == 1

        assert (
            action.external_id
            == "plink_agent_test_001"
        )

        # ------------------------------------------------
        # RECOVERY CASE UPDATED
        # ------------------------------------------------

        db.refresh(recovery_case)

        assert recovery_case.attempts == 1

    finally:

        db.query(
            RecoveryAction
        ).filter(
            RecoveryAction.recovery_case_id
            == recovery_case.id
        ).delete(
            synchronize_session=False
        )

        db.delete(recovery_case)
        db.delete(payment)

        db.commit()
        db.close()