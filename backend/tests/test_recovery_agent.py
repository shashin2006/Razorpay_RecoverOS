from datetime import datetime, timezone
from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
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
                        )(),
                    },
                )(),
            ],
        },
    )()


def test_agent_cannot_bypass_recovery_policy():

    db = SessionLocal()

    payment_id = (
        "pay_agent_policy_test_001"
    )

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id=(
            "order_agent_policy_test_001"
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

        # ------------------------------------------------
        # Simulate malicious LLM request.
        # ------------------------------------------------

        malicious_call = _tool_call(
            "call_policy_1",
            "execute_bounded_recovery",
            (
                '{"recovery_case_id": '
                f"{recovery_case.id}, "
                '"action": "retry_payment"}'
            ),
        )

        responses = [
            _response(
                tool_calls=[malicious_call]
            ),
            _response(
                content=(
                    "The requested recovery action "
                    "was blocked by RecoveryOS policy."
                )
            ),
        ]

        with patch(
            "app.services.llm.recovery_agent.client.chat.completions.create",
            side_effect=responses,
        ):

            # ------------------------------------------------
            # Mock only the final content-safety layer.
            # The agent/policy logic remains real.
            # ------------------------------------------------

            with patch(
                "app.services.llm.recovery_agent.make_safe_customer_message"
            ) as mock_safety:

                mock_safety.return_value = {
                    "message": (
                        "The requested recovery action "
                        "was blocked by RecoveryOS policy."
                    ),
                    "safe": True,
                    "reason": (
                        "Test safety validation passed."
                    ),
                    "fallback_used": False,
                }

                # ------------------------------------------------
                # The real RecoveryOS agent executes.
                # ------------------------------------------------

                with patch(
                    "app.services.llm.agent_tools.execute_recovery_action"
                ) as mock_execute:

                    result = run_recovery_agent(
                        db=db,
                        recovery_case_id=(
                            recovery_case.id
                        ),
                    )

        # ------------------------------------------------
        # AGENT SHOULD FINISH NORMALLY
        # ------------------------------------------------

        assert result["status"] == "completed"

        assert (
            result["agent_assessment"]
            == "The requested recovery action "
               "was blocked by RecoveryOS policy."
        )

        # Only the malicious tool request happened.
        assert len(
            result["tool_calls"]
        ) == 1

        # ------------------------------------------------
        # POLICY MUST REJECT retry_payment
        # ------------------------------------------------

        tool_result = (
            result["tool_calls"][0]["result"]
        )

        assert (
            tool_result["executed"]
            is False
        )

        assert (
            "does not match the approved recovery policy"
            in tool_result["reason"]
        )

        # ------------------------------------------------
        # REAL EXECUTOR MUST NEVER RUN
        # ------------------------------------------------

        mock_execute.assert_not_called()

        # ------------------------------------------------
        # CASE MUST REMAIN UNCHANGED
        # ------------------------------------------------

        db.refresh(recovery_case)

        assert recovery_case.attempts == 0

        assert (
            recovery_case.status
            == "open"
        )

        # ------------------------------------------------
        # SAFETY LAYER WAS CALLED
        # ------------------------------------------------

        mock_safety.assert_called_once()

    finally:

        db.delete(recovery_case)
        db.delete(payment)

        db.commit()
        db.close()