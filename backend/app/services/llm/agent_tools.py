from sqlalchemy.orm import Session

from app.db.models import MLPrediction, Payment, RecoveryAction, RecoveryCase
from app.services.action_executor import execute_recovery_action
from app.services.recovery_policy import determine_recovery_action


def inspect_recovery_case(db: Session, recovery_case_id: int) -> dict:
    """Read-only RecoveryOS agent tool."""
    recovery_case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == recovery_case_id)
        .first()
    )

    if recovery_case is None:
        return {"found": False, "error": "Recovery case not found."}

    payment = (
        db.query(Payment)
        .filter(Payment.provider_payment_id == recovery_case.payment_id)
        .first()
    )

    action = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.recovery_case_id == recovery_case.id)
        .order_by(RecoveryAction.id.desc())
        .first()
    )

    prediction = (
        db.query(MLPrediction)
        .filter(MLPrediction.recovery_case_id == recovery_case.id)
        .order_by(MLPrediction.id.desc())
        .first()
    )

    policy = determine_recovery_action(recovery_case)

    return {
        "found": True,
        "recovery_case": {
            "id": recovery_case.id,
            "status": recovery_case.status,
            "failure_category": recovery_case.failure_category,
            "attempts": recovery_case.attempts,
            "amount_at_risk_minor": recovery_case.amount_at_risk_minor,
            "amount_recovered": recovery_case.amount_recovered,
            "currency": recovery_case.currency,
        },
        "payment": {
            "provider": payment.provider if payment else None,
            "payment_id": payment.provider_payment_id if payment else None,
            "amount_minor": payment.amount_minor if payment else None,
            "currency": payment.currency if payment else None,
            "method": payment.method if payment else None,
            "status": payment.status if payment else None,
            "error_code": payment.error_code if payment else None,
            "error_source": payment.error_source if payment else None,
            "error_step": payment.error_step if payment else None,
            "error_reason": payment.error_reason if payment else None,
        },
        "latest_action": (
            {
                "action_type": action.action_type,
                "status": action.status,
                "attempt_number": action.attempt_number,
            }
            if action else None
        ),
        "ml_prediction": (
            {
                "probability": prediction.probability,
                "threshold": prediction.threshold,
                "recommendation": prediction.recommendation,
                "model_version": prediction.model_version,
                "mode": prediction.mode,
            }
            if prediction else None
        ),
        "policy": {
            "eligible": policy.eligible,
            "action": policy.action.value,
            "max_attempts": policy.max_attempts,
            "cooldown_minutes": policy.cooldown_minutes,
            "reason": policy.reason,
        },
    }


def execute_bounded_recovery(
    db: Session,
    recovery_case_id: int,
    action: str,
) -> dict:
    recovery_case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == recovery_case_id)
        .first()
    )

    if recovery_case is None:
        return {"executed": False, "reason": "Recovery case not found."}

    policy = determine_recovery_action(recovery_case)

    if not policy.eligible:
        return {
            "executed": False,
            "reason": "Recovery policy does not permit automated action.",
            "policy_action": policy.action.value,
        }

    if recovery_case.status != "open":
        return {"executed": False, "reason": "Recovery case is not open."}

    if recovery_case.amount_recovered > 0:
        return {"executed": False, "reason": "Revenue has already been recovered."}

    if recovery_case.attempts >= policy.max_attempts:
        return {
            "executed": False,
            "reason": "Maximum recovery attempts reached.",
            "max_attempts": policy.max_attempts,
        }

    if action != policy.action.value:
        return {
            "executed": False,
            "reason": "Requested action does not match the approved recovery policy.",
            "requested_action": action,
            "approved_action": policy.action.value,
        }

    result = execute_recovery_action(
        db=db,
        recovery_case=recovery_case,
        action=action,
        reason=policy.reason,
        max_attempts=policy.max_attempts,
    )

    return {
        "executed": result.status.value == "created",
        "status": result.status.value,
        "action": result.action,
        "external_id": result.external_id,
        "payment_link_url": result.payment_link_url,
        "message": result.message,
    }
