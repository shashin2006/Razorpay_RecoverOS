from dataclasses import dataclass

from app.services.failure_classifier import (
    FailureClassification,
    Recoverability,
)


@dataclass
class RevenueRisk:
    amount_at_risk_minor: int
    recoverable: bool
    reason: str


def calculate_revenue_risk(
    amount_minor: int,
    classification: FailureClassification,
) -> RevenueRisk:

    if (
        classification.recoverability
        == Recoverability.RECOVERABLE
    ):
        return RevenueRisk(
            amount_at_risk_minor=amount_minor,
            recoverable=True,
            reason=(
                "Payment failed but the failure "
                "is potentially recoverable."
            ),
        )

    return RevenueRisk(
        amount_at_risk_minor=0,
        recoverable=False,
        reason=(
            "Payment failure is not currently "
            "eligible for automated recovery."
        ),
    )