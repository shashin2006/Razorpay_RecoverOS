from sqlalchemy.orm import Session

from app.db.models import (
    MLPrediction,
    Payment,
    RecoveryAction,
    RecoveryCase,
)

from app.services.recovery_policy import (
    determine_recovery_action,
)

from app.services.action_executor import (
    execute_recovery_action,
)


def inspect_recovery_case(
    db: Session,
    recovery_case_id: int,
) -> dict:
    """
    Read-only tool for the RecoveryOS agent.

    Provides the agent with the authoritative state of:
    - Recovery case
    - Payment
    - Latest recovery action
    - Latest ML prediction
    - Deterministic recovery policy

    This function does not modify the database
    and does not execute any financial action.
    """

    recovery_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.id
            == recovery_case_id
        )
        .first()
    )

    if recovery_case is None:
        return {
            "found": False,
            "error": "Recovery case not found.",
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_payment_id
            == recovery_case.payment_id
        )
        .first()
    )

    action = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.recovery_case_id
            == recovery_case.id
        )
        .order_by(
            RecoveryAction.id.desc()
        )
        .first()
    )

    prediction = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.recovery_case_id
            == recovery_case.id
        )
        .order_by(
            MLPrediction.id.desc()
        )
        .first()
    )

    policy = determine_recovery_action(
        recovery_case
    )

    return {
        "found": True,

        # ----------------------------------------
        # RECOVERY CASE
        # ----------------------------------------

        "recovery_case": {
            "id": recovery_case.id,
            "status": recovery_case.status,
            "failure_category": (
                recovery_case.failure_category
            ),
            "attempts": recovery_case.attempts,
            "amount_at_risk_minor": (
                recovery_case.amount_at_risk_minor
            ),
            "amount_recovered": (
                recovery_case.amount_recovered
            ),
            "currency": recovery_case.currency,
        },

        # ----------------------------------------
        # PAYMENT
        # ----------------------------------------

        "payment": {
            "payment_id": (
                payment.razorpay_payment_id
                if payment
                else None
            ),
            "amount_minor": (
                payment.amount_minor
                if payment
                else None
            ),
            "currency": (
                payment.currency
                if payment
                else None
            ),
            "method": (
                payment.method
                if payment
                else None
            ),
            "status": (
                payment.status
                if payment
                else None
            ),
            "error_code": (
                payment.error_code
                if payment
                else None
            ),
            "error_source": (
                payment.error_source
                if payment
                else None
            ),
            "error_step": (
                payment.error_step
                if payment
                else None
            ),
            "error_reason": (
                payment.error_reason
                if payment
                else None
            ),
        },

        # ----------------------------------------
        # LATEST RECOVERY ACTION
        # ----------------------------------------

        "latest_action": (
            {
                "action_type": action.action_type,
                "status": action.status,
                "attempt_number": (
                    action.attempt_number
                ),
            }
            if action
            else None
        ),

        # ----------------------------------------
        # ML PREDICTION
        # ----------------------------------------

        "ml_prediction": (
            {
                "probability": prediction.probability,
                "threshold": prediction.threshold,
                "recommendation": (
                    prediction.recommendation
                ),
                "model_version": (
                    prediction.model_version
                ),
                "mode": prediction.mode,
            }
            if prediction
            else None
        ),

        # ----------------------------------------
        # DETERMINISTIC POLICY
        # ----------------------------------------

        "policy": {
            "eligible": policy.eligible,
            "action": policy.action.value,
            "max_attempts": policy.max_attempts,
            "cooldown_minutes": (
                policy.cooldown_minutes
            ),
            "reason": policy.reason,
        },
    }


def execute_bounded_recovery(
    db: Session,
    recovery_case_id: int,
    action: str,
) -> dict:
    """
    Execute a recovery action requested by the agent.

    IMPORTANT:
    The LLM does NOT control execution directly.

    Every requested action passes through the deterministic
    RecoveryOS policy before the existing action executor
    is allowed to run.

    Safety guarantees:
    - Case must exist.
    - Case must be open.
    - Revenue must not already be recovered.
    - Policy must allow automated recovery.
    - Requested action must match the approved policy action.
    - Maximum attempt limit must not be exceeded.
    - Actual execution is delegated to the existing
      action executor.
    """

    # ----------------------------------------
    # LOAD RECOVERY CASE
    # ----------------------------------------

    recovery_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.id
            == recovery_case_id
        )
        .first()
    )

    if recovery_case is None:
        return {
            "executed": False,
            "reason": "Recovery case not found.",
        }

    # ----------------------------------------
    # GET DETERMINISTIC POLICY
    # ----------------------------------------

    policy = determine_recovery_action(
        recovery_case
    )

    # ----------------------------------------
    # HARD SAFETY GATE #1
    # POLICY ELIGIBILITY
    # ----------------------------------------

    if not policy.eligible:
        return {
            "executed": False,
            "reason": (
                "Recovery policy does not permit "
                "automated action."
            ),
            "policy_action": (
                policy.action.value
            ),
        }

    # ----------------------------------------
    # HARD SAFETY GATE #2
    # CASE MUST BE OPEN
    # ----------------------------------------

    if recovery_case.status != "open":
        return {
            "executed": False,
            "reason": (
                "Recovery case is not open."
            ),
        }

    # ----------------------------------------
    # HARD SAFETY GATE #3
    # REVENUE MUST NOT ALREADY BE RECOVERED
    # ----------------------------------------

    if recovery_case.amount_recovered > 0:
        return {
            "executed": False,
            "reason": (
                "Revenue has already been recovered."
            ),
        }

    # ----------------------------------------
    # HARD SAFETY GATE #4
    # MAXIMUM ATTEMPTS
    # ----------------------------------------

    if (
        recovery_case.attempts
        >= policy.max_attempts
    ):
        return {
            "executed": False,
            "reason": (
                "Maximum recovery attempts reached."
            ),
            "max_attempts": policy.max_attempts,
        }

    # ----------------------------------------
    # HARD SAFETY GATE #5
    # ACTION MUST MATCH POLICY
    # ----------------------------------------

    if action != policy.action.value:
        return {
            "executed": False,
            "reason": (
                "Requested action does not match "
                "the approved recovery policy."
            ),
            "requested_action": action,
            "approved_action": (
                policy.action.value
            ),
        }

    # ----------------------------------------
    # EXECUTE THROUGH EXISTING EXECUTOR
    # ----------------------------------------

    result = execute_recovery_action(
        db=db,
        recovery_case=recovery_case,
        action=action,
        reason=policy.reason,
        max_attempts=policy.max_attempts,
    )

    # ----------------------------------------
    # RETURN EXECUTION RESULT
    # ----------------------------------------

    return {
        "executed": (
            result.status.value
            == "created"
        ),
        "status": result.status.value,
        "action": result.action,
        "external_id": result.external_id,
        "payment_link_url": (
            result.payment_link_url
        ),
        "message": result.message,
    }