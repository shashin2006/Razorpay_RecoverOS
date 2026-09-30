from dataclasses import dataclass
from enum import Enum

from app.db.models import RecoveryCase
from app.services.failure_classifier import FailureCategory


class RecoveryAction(str, Enum):
    RETRY_PAYMENT = "retry_payment"
    ALTERNATE_PAYMENT_METHOD = "alternate_payment_method"
    CUSTOMER_REMINDER = "customer_reminder"
    ESCALATE = "escalate"
    NO_ACTION = "no_action"


@dataclass
class RecoveryDecision:
    eligible: bool
    action: RecoveryAction
    max_attempts: int
    cooldown_minutes: int
    reason: str


def determine_recovery_action(
    recovery_case: RecoveryCase,
) -> RecoveryDecision:

    if recovery_case.status != "open":
        return RecoveryDecision(
            eligible=False,
            action=RecoveryAction.NO_ACTION,
            max_attempts=0,
            cooldown_minutes=0,
            reason="Recovery case is not open.",
        )

    if recovery_case.attempts >= 2:
        return RecoveryDecision(
            eligible=False,
            action=RecoveryAction.ESCALATE,
            max_attempts=2,
            cooldown_minutes=0,
            reason="Maximum automated recovery attempts reached.",
        )

    if (
        recovery_case.failure_category
        == FailureCategory.BANK_DECLINE.value
    ):
        return RecoveryDecision(
            eligible=True,
            action=RecoveryAction.ALTERNATE_PAYMENT_METHOD,
            max_attempts=2,
            cooldown_minutes=30,
            reason=(
                "Bank authorization decline is potentially "
                "recoverable through an alternate payment method."
            ),
        )

    return RecoveryDecision(
        eligible=False,
        action=RecoveryAction.NO_ACTION,
        max_attempts=0,
        cooldown_minutes=0,
        reason="No approved recovery policy exists for this failure.",
    )