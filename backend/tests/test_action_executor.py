from unittest.mock import patch

from app.services.action_executor import (
    ActionExecutionStatus,
    execute_action,
)


@patch(
    "app.services.action_executor.create_recovery_payment_link"
)
def test_alternate_payment_action_is_created(
    mock_create_link,
):

    mock_create_link.return_value = {
        "id": "plink_test_001",
        "short_url": "https://rzp.io/test",
    }

    result = execute_action(
        action="alternate_payment_method",
        amount_minor=50000,
        currency="INR",
        recovery_case_id=1,
    )

    assert result.status == ActionExecutionStatus.CREATED
    assert result.action == "alternate_payment_method"
    assert result.external_id == "plink_test_001"

    mock_create_link.assert_called_once()


def test_unknown_action_is_skipped():

    result = execute_action(
        action="something_not_allowed",
        amount_minor=50000,
        currency="INR",
        recovery_case_id=1,
    )

    assert result.status == ActionExecutionStatus.SKIPPED