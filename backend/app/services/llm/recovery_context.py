from app.db.models import (
    Payment,
    RecoveryAction,
    RecoveryCase,
    MLPrediction,
)


def build_recovery_context(
    payment: Payment,
    recovery_case: RecoveryCase,
    recovery_action: RecoveryAction | None = None,
    prediction: MLPrediction | None = None,
    policy_decision=None,
) -> dict:

    context = {
        "payment": {
            "payment_id": payment.razorpay_payment_id,
            "order_id": payment.razorpay_order_id,
            "amount_minor": payment.amount_minor,
            "currency": payment.currency,
            "method": payment.method,
            "status": payment.status,
            "error_code": payment.error_code,
            "error_source": payment.error_source,
            "error_step": payment.error_step,
            "error_reason": payment.error_reason,
        },

        "recovery_case": {
            "id": recovery_case.id,
            "failure_category": (
                recovery_case.failure_category
            ),
            "status": recovery_case.status,
            "attempts": recovery_case.attempts,
            "amount_at_risk_minor": (
                recovery_case.amount_at_risk_minor
            ),
            "amount_recovered": (
                recovery_case.amount_recovered
            ),
            "currency": recovery_case.currency,
        },
    }

    if recovery_action is not None:
        context["recovery_action"] = {
            "action_type": recovery_action.action_type,
            "status": recovery_action.status,
            "attempt_number": (
                recovery_action.attempt_number
            ),
            "reason": recovery_action.reason,
        }

    if prediction is not None:
        context["ml_prediction"] = {
            "probability": prediction.probability,
            "threshold": prediction.threshold,
            "recommendation": (
                prediction.recommendation
            ),
            "model_version": prediction.model_version,
            "mode": prediction.mode,
            "outcome_recorded": (
                prediction.outcome_recorded
            ),
            "actual_recovered": (
                prediction.actual_recovered
            ),
        }

    if policy_decision is not None:
        context["recovery_policy"] = {
            "eligible": policy_decision.eligible,
            "action": policy_decision.action.value,
            "max_attempts": (
                policy_decision.max_attempts
            ),
            "cooldown_minutes": (
                policy_decision.cooldown_minutes
            ),
            "reason": policy_decision.reason,
        }

    return context