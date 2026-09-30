from sqlalchemy.orm import Session

from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
    Payment,
    RecoveryAction,
    RecoveryCase,
)


def build_recovery_context(
    db: Session,
    recovery_case_id: int,
) -> dict:

    recovery_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.id
            == recovery_case_id
        )
        .first()
    )

    if recovery_case is None:
        raise ValueError(
            f"Recovery case {recovery_case_id} not found."
        )

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
            == recovery_case_id
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
            == recovery_case_id
        )
        .order_by(
            MLPrediction.id.desc()
        )
        .first()
    )

    audit = (
        db.query(MLDecisionAudit)
        .filter(
            MLDecisionAudit.recovery_case_id
            == recovery_case_id
        )
        .order_by(
            MLDecisionAudit.id.desc()
        )
        .first()
    )

    return {
        "case": {
            "id": recovery_case.id,
            "status": recovery_case.status,
            "amount_at_risk_minor": (
                recovery_case.amount_at_risk_minor
            ),
            "amount_recovered": (
                recovery_case.amount_recovered
            ),
            "currency": recovery_case.currency,
            "failure_category": (
                recovery_case.failure_category
            ),
            "attempts": recovery_case.attempts,
        },
        "payment": (
            {
                "payment_id": (
                    payment.razorpay_payment_id
                ),
                "amount_minor": payment.amount_minor,
                "currency": payment.currency,
                "method": payment.method,
                "status": payment.status,
                "error_code": payment.error_code,
                "error_source": payment.error_source,
                "error_step": payment.error_step,
                "error_reason": payment.error_reason,
            }
            if payment
            else None
        ),
        "action": (
            {
                "action_type": action.action_type,
                "status": action.status,
                "attempt_number": (
                    action.attempt_number
                ),
                "reason": action.reason,
            }
            if action
            else None
        ),
        "ml": (
            {
                "probability": prediction.probability,
                "threshold": prediction.threshold,
                "recommendation": (
                    prediction.recommendation
                ),
                "model_version": (
                    prediction.model_version
                ),
                "outcome_recorded": (
                    prediction.outcome_recorded
                ),
                "actual_recovered": (
                    prediction.actual_recovered
                ),
            }
            if prediction
            else None
        ),
        "decision_audit": (
            {
                "policy_eligible": (
                    audit.policy_eligible
                ),
                "policy_action": (
                    audit.policy_action
                ),
                "ml_probability": (
                    audit.ml_probability
                ),
                "ml_threshold": (
                    audit.ml_threshold
                ),
                "ml_recommendation": (
                    audit.ml_recommendation
                ),
                "agreement": audit.agreement,
            }
            if audit
            else None
        ),
    }