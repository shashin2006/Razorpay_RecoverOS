from app.services.failure_classifier import (
    FailureCategory,
    Recoverability,
    classify_failure,
)


def test_bank_decline_is_recoverable():

    payment = {
        "error_source": "bank",
        "error_step": "payment_authorization",
        "error_reason": "payment_failed",
        "error_code": "BAD_REQUEST_ERROR",
    }

    result = classify_failure(payment)

    assert result.category == FailureCategory.BANK_DECLINE

    assert (
        result.recoverability
        == Recoverability.RECOVERABLE
    )

    assert result.customer_action_required is True


def test_unknown_failure_is_not_assumed_recoverable():

    payment = {
        "error_source": "something_unknown",
        "error_step": "unknown_step",
        "error_reason": "unknown_reason",
        "error_code": "UNKNOWN_ERROR",
    }

    result = classify_failure(payment)

    assert result.category == FailureCategory.UNKNOWN

    assert (
        result.recoverability
        == Recoverability.UNKNOWN
    )

    assert result.customer_action_required is False