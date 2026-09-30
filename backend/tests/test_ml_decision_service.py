from unittest.mock import MagicMock, patch

from app.services.ml_decision_service import (
    evaluate_ml_against_policy,
)


def test_ml_and_policy_agree():

    db = MagicMock()

    payment = MagicMock()
    recovery_case = MagicMock()
    recovery_action = MagicMock()

    recovery_case.id = 1
    recovery_case.status = "open"
    recovery_case.attempts = 1
    recovery_case.failure_category = "bank_decline"

    payment.amount_minor = 50000
    payment.currency = "INR"
    payment.method = "netbanking"

    payment.error_source = "bank"
    payment.error_step = "payment_authorization"
    payment.error_reason = "payment_failed"
    payment.error_code = "BAD_REQUEST_ERROR"

    recovery_action.action_type = (
        "alternate_payment_method"
    )
    recovery_action.attempt_number = 1

    mock_prediction = MagicMock()

    mock_prediction.probability = 0.69
    mock_prediction.threshold = 0.40
    mock_prediction.recommendation = True

    from unittest.mock import patch

    with patch(
        "app.services.ml_decision_service.record_shadow_prediction",
        return_value=mock_prediction,
    ):

        result = evaluate_ml_against_policy(
            db=db,
            payment=payment,
            recovery_case=recovery_case,
            recovery_action=recovery_action,
        )

    assert result.policy_eligible is True
    assert result.policy_action == (
        "alternate_payment_method"
    )

    assert result.ml_probability == 0.69
    assert result.ml_recommendation is True
    assert result.threshold == 0.40

    assert result.agreement is True

def test_ml_and_policy_disagree():

    db = MagicMock()

    payment = MagicMock()
    recovery_case = MagicMock()
    recovery_action = MagicMock()

    recovery_case.id = 2
    recovery_case.status = "open"
    recovery_case.attempts = 1
    recovery_case.failure_category = "bank_decline"

    payment.amount_minor = 50000
    payment.currency = "INR"
    payment.method = "netbanking"

    payment.error_source = "bank"
    payment.error_step = "payment_authorization"
    payment.error_reason = "payment_failed"
    payment.error_code = "BAD_REQUEST_ERROR"

    recovery_action.action_type = (
        "alternate_payment_method"
    )
    recovery_action.attempt_number = 1

    mock_prediction = MagicMock()

    mock_prediction.probability = 0.30
    mock_prediction.threshold = 0.40
    mock_prediction.recommendation = False

    with patch(
        "app.services.ml_decision_service.record_shadow_prediction",
        return_value=mock_prediction,
    ):

        result = evaluate_ml_against_policy(
            db=db,
            payment=payment,
            recovery_case=recovery_case,
            recovery_action=recovery_action,
        )

    assert result.policy_eligible is True

    assert result.policy_action == (
        "alternate_payment_method"
    )

    assert result.ml_probability == 0.30
    assert result.ml_recommendation is False
    assert result.threshold == 0.40

    assert result.agreement is False