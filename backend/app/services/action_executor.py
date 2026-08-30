from dataclasses import dataclass
from enum import Enum

from app.services.payment_link import (
    create_recovery_payment_link,
)


class ActionExecutionStatus(str, Enum):
    CREATED = "created"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class ActionExecutionResult:
    status: ActionExecutionStatus
    action: str
    external_id: str | None
    message: str


def execute_action(
    action: str,
    amount_minor: int,
    currency: str,
    recovery_case_id: int,
) -> ActionExecutionResult:

    if action == "alternate_payment_method":

        try:

            payment_link = create_recovery_payment_link(
                amount_minor=amount_minor,
                currency=currency,
                description="RecoveryOS Revenue Recovery",
                recovery_case_id=recovery_case_id,
            )

            return ActionExecutionResult(
                status=ActionExecutionStatus.CREATED,
                action=action,
                external_id=payment_link["id"],
                message=(
                    "Recovery payment link created."
                ),
            )

        except Exception as exc:

            return ActionExecutionResult(
                status=ActionExecutionStatus.FAILED,
                action=action,
                external_id=None,
                message=str(exc),
            )

    return ActionExecutionResult(
        status=ActionExecutionStatus.SKIPPED,
        action=action,
        external_id=None,
        message="Action is not currently executable.",
    )