from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import RecoveryCase
from app.services.action_executor import (
    ActionExecutionStatus,
    execute_recovery_action,
)


def create_case(db, *, status="open", attempts=0):
    case = RecoveryCase(
        payment_id=f"pay_executor_test_{id(object())}",
        amount_at_risk_minor=50000,
        currency="INR",
        failure_category="bank_decline",
        status=status,
        attempts=attempts,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


@patch(
    "app.services.action_executor.create_recovery_payment_link"
)
def test_valid_recovery_action_is_created(mock_create_link):
    db = SessionLocal()

    mock_create_link.return_value = {
        "id": "plink_executor_test_001",
        "short_url": "https://rzp.io/test",
    }

    case = create_case(db)

    try:
        result = execute_recovery_action(
            db=db,
            recovery_case=case,
            action="alternate_payment_method",
            reason="Bank decline is recoverable.",
            max_attempts=2,
        )

        assert result.status == ActionExecutionStatus.CREATED
        assert result.action == "alternate_payment_method"
        assert result.external_id == "plink_executor_test_001"

        db.refresh(case)

        assert case.attempts == 1

        mock_create_link.assert_called_once()

    finally:
        db.delete(case)
        db.commit()
        db.close()


def test_closed_case_cannot_be_recovered():
    db = SessionLocal()

    case = create_case(
        db,
        status="recovered",
        attempts=0,
    )

    try:
        result = execute_recovery_action(
            db=db,
            recovery_case=case,
            action="alternate_payment_method",
            reason="Test recovery.",
            max_attempts=2,
        )

        assert result.status == ActionExecutionStatus.SKIPPED
        assert result.external_id is None
        assert "no longer open" in result.message

    finally:
        db.delete(case)
        db.commit()
        db.close()


def test_second_attempt_is_allowed():
    db = SessionLocal()

    case = create_case(
        db,
        status="open",
        attempts=1,
    )

    try:
        with patch(
            "app.services.action_executor.create_recovery_payment_link"
        ) as mock_create_link:

            mock_create_link.return_value = {
                "id": "plink_executor_test_002",
                "short_url": "https://rzp.io/test",
            }

            result = execute_recovery_action(
                db=db,
                recovery_case=case,
                action="alternate_payment_method",
                reason="Second bounded recovery attempt.",
                max_attempts=2,
            )

        assert result.status == ActionExecutionStatus.CREATED

        db.refresh(case)

        assert case.attempts == 2

    finally:
        db.delete(case)
        db.commit()
        db.close()


def test_third_attempt_is_blocked():
    db = SessionLocal()

    case = create_case(
        db,
        status="open",
        attempts=2,
    )

    try:
        with patch(
            "app.services.action_executor.create_recovery_payment_link"
        ) as mock_create_link:

            result = execute_recovery_action(
                db=db,
                recovery_case=case,
                action="alternate_payment_method",
                reason="Should be blocked.",
                max_attempts=2,
            )

        assert result.status == ActionExecutionStatus.SKIPPED
        assert "Maximum recovery attempts reached" in result.message

        mock_create_link.assert_not_called()

    finally:
        db.delete(case)
        db.commit()
        db.close()


def test_caller_cannot_override_two_attempt_safety_ceiling():
    db = SessionLocal()

    case = create_case(
        db,
        status="open",
        attempts=2,
    )

    try:
        with patch(
            "app.services.action_executor.create_recovery_payment_link"
        ) as mock_create_link:

            result = execute_recovery_action(
                db=db,
                recovery_case=case,
                action="alternate_payment_method",
                reason="Attempt to bypass safety limit.",
                max_attempts=100,
            )

        assert result.status == ActionExecutionStatus.SKIPPED
        assert "Maximum recovery attempts reached" in result.message

        mock_create_link.assert_not_called()

    finally:
        db.delete(case)
        db.commit()
        db.close()