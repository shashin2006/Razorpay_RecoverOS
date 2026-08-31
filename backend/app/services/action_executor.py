from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session

from app.db.models import RecoveryCase
from app.services.action_audit import record_action
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
    payment_link_url: str | None
    message: str


def execute_recovery_action(
    db: Session,
    recovery_case: RecoveryCase,
    action: str,
    reason: str,
    max_attempts: int,
) -> ActionExecutionResult:

    # ----------------------------------------
    # PRE-EXECUTION GUARD 1
    # ----------------------------------------

    if recovery_case.status != "open":

        return ActionExecutionResult(
            status=ActionExecutionStatus.SKIPPED,
            action=action,
            external_id=None,
            payment_link_url=None,
            message="Recovery case is no longer open.",
        )

    # ----------------------------------------
    # PRE-EXECUTION GUARD 2
    # ----------------------------------------

    if recovery_case.attempts >= max_attempts:

        return ActionExecutionResult(
            status=ActionExecutionStatus.SKIPPED,
            action=action,
            external_id=None,
            payment_link_url=None,
            message="Maximum recovery attempts reached.",
        )

    # ----------------------------------------
    # CREATE PAYMENT LINK
    # ----------------------------------------

    if action == "alternate_payment_method":

        attempt_number = recovery_case.attempts + 1

        try:

            payment_link = create_recovery_payment_link(
                amount_minor=recovery_case.amount_at_risk_minor,
                currency=recovery_case.currency,
                description="RecoveryOS Revenue Recovery",
                recovery_case_id=recovery_case.id,
            )
            print("Razorpay Payment Link:", payment_link)

            # ----------------------------------------
            # UPDATE CASE
            # ----------------------------------------

            recovery_case.attempts = attempt_number

            # ----------------------------------------
            # AUDIT ACTION
            # ----------------------------------------

            record_action(
                db=db,
                recovery_case_id=recovery_case.id,
                action_type=action,
                status="executed",
                attempt_number=attempt_number,
                reason=reason,
                external_id=payment_link["id"],
                payment_link_url=payment_link.get("short_url"),
            )

            db.commit()

            return ActionExecutionResult(
                status=ActionExecutionStatus.CREATED,
                action=action,
                external_id=payment_link["id"],
                payment_link_url=payment_link.get("short_url"),
                message="Recovery payment link created.",
            )

        except Exception as exc:

            db.rollback()

            return ActionExecutionResult(
                status=ActionExecutionStatus.FAILED,
                action=action,
                external_id=None,
                payment_link_url=None,
                message=str(exc),
            )

    return ActionExecutionResult(
        status=ActionExecutionStatus.SKIPPED,
        action=action,
        external_id=None,
        payment_link_url=None,
        message="Action is not currently executable.",
    )

def execute_action(
    action: str,
    amount_minor: int,
    currency: str,
    recovery_case_id: int,
) -> ActionExecutionResult:

    if action != "alternate_payment_method":
        return ActionExecutionResult(
            status=ActionExecutionStatus.SKIPPED,
            action=action,
            external_id=None,
            payment_link_url=None,
            message="Action is not currently executable.",
        )

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
        payment_link_url=payment_link.get("short_url"),
        message="Recovery payment link created.",
    )