from app.services.failure_classifier import (
    FailureCategory,
    FailureClassification,
    Recoverability,
)

from app.services.risk_engine import (
    calculate_revenue_risk,
)


def test_recoverable_payment_creates_revenue_risk():

    classification = FailureClassification(
        category=FailureCategory.BANK_DECLINE,
        recoverability=Recoverability.RECOVERABLE,
        customer_action_required=True,
        reason="Bank declined payment.",
    )

    result = calculate_revenue_risk(
        amount_minor=50000,
        classification=classification,
    )

    assert result.amount_at_risk_minor == 50000
    assert result.recoverable is True


def test_non_recoverable_payment_has_no_automated_risk():

    classification = FailureClassification(
        category=FailureCategory.UNKNOWN,
        recoverability=Recoverability.NOT_RECOVERABLE,
        customer_action_required=False,
        reason="Permanent failure.",
    )

    result = calculate_revenue_risk(
        amount_minor=50000,
        classification=classification,
    )

    assert result.amount_at_risk_minor == 0
    assert result.recoverable is False