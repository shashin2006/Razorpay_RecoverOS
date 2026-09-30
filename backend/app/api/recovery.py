from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    MLDecisionAudit,
    MLPrediction,
    Payment,
    RecoveryAction,
    RecoveryCase,
)
from app.services.recovery_policy import determine_recovery_action


router = APIRouter(
    prefix="/api/recovery",
    tags=["Recovery Cases"],
)


@router.get("/cases")
def get_recovery_cases(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(RecoveryCase)
        .order_by(RecoveryCase.created_at.desc())
        .all()
    )

    return {
        "cases": [
            {
                "id": case.id,
                "payment_id": case.payment_id,
                "amount_at_risk_minor": case.amount_at_risk_minor,
                "currency": case.currency,
                "failure_category": case.failure_category,
                "status": case.status,
                "attempts": case.attempts,
                "amount_recovered": case.amount_recovered,
                "created_at": case.created_at,
                "updated_at": case.updated_at,
            }
            for case in cases
        ],
        "total": len(cases),
    }


@router.get("/cases/{recovery_case_id}")
def get_recovery_case(
    recovery_case_id: int,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == recovery_case_id)
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found.",
        )

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_payment_id == case.payment_id
        )
        .first()
    )


    latest_action = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.recovery_case_id == case.id
        )
        .order_by(RecoveryAction.created_at.desc())
        .first()
    )


    latest_ml_prediction = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.recovery_case_id == case.id
        )
        .order_by(MLPrediction.created_at.desc())
        .first()
    )

    latest_decision_audit = (
        db.query(MLDecisionAudit)
        .filter(
            MLDecisionAudit.recovery_case_id == case.id
        )
        .order_by(MLDecisionAudit.created_at.desc())
        .first()
    )

    policy_decision = determine_recovery_action(
        recovery_case=case
    )

    return {
        "case": {
            "id": case.id,
            "payment_id": case.payment_id,
            "amount_at_risk_minor": case.amount_at_risk_minor,
            "currency": case.currency,
            "failure_category": case.failure_category,
            "status": case.status,
            "attempts": case.attempts,
            "amount_recovered": case.amount_recovered,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
        },

        "payment": (
            {
                "razorpay_payment_id": payment.razorpay_payment_id,
                "razorpay_order_id": payment.razorpay_order_id,
                "amount_minor": payment.amount_minor,
                "currency": payment.currency,
                "method": payment.method,
                "status": payment.status,
                "error_code": payment.error_code,
                "error_step": payment.error_step,
                "error_reason": payment.error_reason,
                "error_source": payment.error_source,
                "error_description": payment.error_description,
                "created_at": payment.created_at,
                "updated_at": payment.updated_at,
            }
            if payment
            else None
        ),

        "latest_action": (
            {
                "id": latest_action.id,
                "action_type": latest_action.action_type,
                "status": latest_action.status,
                "attempt_number": latest_action.attempt_number,
                "reason": latest_action.reason,
                "external_id": latest_action.external_id,
                "payment_link_url": latest_action.payment_link_url,
                "created_at": latest_action.created_at,
                "executed_at": latest_action.executed_at,
            }
            if latest_action
            else None
        ),


        "latest_ml_prediction": (
            {
                "id": latest_ml_prediction.id,
                "probability": latest_ml_prediction.probability,
                "threshold": latest_ml_prediction.threshold,
                "recommendation": latest_ml_prediction.recommendation,
                "model_version": latest_ml_prediction.model_version,
                "mode": latest_ml_prediction.mode,
                "actual_recovered": latest_ml_prediction.actual_recovered,
                "outcome_recorded": latest_ml_prediction.outcome_recorded,
                "created_at": latest_ml_prediction.created_at,
            }
            if latest_ml_prediction
            else None
        ),

        "policy": {
            "eligible": policy_decision.eligible,
            "action": policy_decision.action.value,
            "max_attempts": policy_decision.max_attempts,
            "cooldown_minutes": policy_decision.cooldown_minutes,
            "reason": policy_decision.reason,
        },

        "decision_audit": (
            {
                "id": latest_decision_audit.id,
                "policy_eligible": latest_decision_audit.policy_eligible,
                "policy_action": latest_decision_audit.policy_action,
                "ml_probability": latest_decision_audit.ml_probability,
                "ml_threshold": latest_decision_audit.ml_threshold,
                "ml_recommendation": latest_decision_audit.ml_recommendation,
                "agreement": latest_decision_audit.agreement,
                "created_at": latest_decision_audit.created_at,
            }
            if latest_decision_audit
            else None
        ),
    }


@router.get("/cases/{recovery_case_id}/audit")
def get_recovery_case_audit(
    recovery_case_id: int,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == recovery_case_id)
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found.",
        )

    events = []

    # --------------------------------------------------
    # Payment
    # --------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_payment_id == case.payment_id
        )
        .first()
    )

    if payment is not None:
        events.append(
            {
                "type": "payment_recorded",
                "timestamp": payment.created_at,
                "status": payment.status,
                "title": "Payment recorded",
                "description": (
                    f"Payment {payment.razorpay_payment_id} "
                    f"was recorded."
                ),
            }
        )

        if payment.status == "failed":
            events.append(
                {
                    "type": "payment_failed",
                    "timestamp": payment.updated_at,
                    "status": "failed",
                    "title": "Payment failed",
                    "description": (
                        payment.error_description
                        or "Payment failure recorded."
                    ),
                }
            )

    # --------------------------------------------------
    # Recovery case
    # --------------------------------------------------

    events.append(
        {
            "type": "recovery_case_created",
            "timestamp": case.created_at,
            "status": "created",
            "title": "Recovery case created",
            "description": (
                f"Recovery case #{case.id} created for "
                f"{case.failure_category}."
            ),
        }
    )

    # --------------------------------------------------
    # ML prediction
    # --------------------------------------------------

    predictions = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.recovery_case_id == case.id
        )
        .order_by(MLPrediction.created_at.asc())
        .all()
    )

    for prediction in predictions:
        events.append(
            {
                "type": "ml_prediction",
                "timestamp": prediction.created_at,
                "status": (
                    "outcome_recorded"
                    if prediction.outcome_recorded
                    else "shadow"
                ),
                "title": "ML prediction generated",
                "description": (
                    f"Recovery probability: "
                    f"{prediction.probability:.1%}. "
                    f"Recommendation: "
                    f"{'recover' if prediction.recommendation else 'do not recover'}."
                ),
            }
        )

    # --------------------------------------------------
    # Policy / ML decision audit
    # --------------------------------------------------

    decision_audits = (
        db.query(MLDecisionAudit)
        .filter(
            MLDecisionAudit.recovery_case_id == case.id
        )
        .order_by(MLDecisionAudit.created_at.asc())
        .all()
    )

    for audit in decision_audits:
        events.append(
            {
                "type": "policy_evaluation",
                "timestamp": audit.created_at,
                "status": (
                    "approved"
                    if audit.policy_eligible
                    else "blocked"
                ),
                "title": "Policy evaluated",
                "description": (
                    f"Policy action: {audit.policy_action}. "
                    f"ML/policy agreement: "
                    f"{'yes' if audit.agreement else 'no'}."
                ),
            }
        )

    # --------------------------------------------------
    # Recovery actions
    # --------------------------------------------------

    actions = (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.recovery_case_id == case.id
        )
        .order_by(RecoveryAction.created_at.asc())
        .all()
    )

    for action in actions:
        events.append(
            {
                "type": "recovery_action",
                "timestamp": action.created_at,
                "status": action.status,
                "title": "Recovery action recorded",
                "description": (
                    f"Action: {action.action_type}. "
                    f"Attempt {action.attempt_number}."
                ),
                "action_type": action.action_type,
                "attempt_number": action.attempt_number,
                "external_id": action.external_id,
                "payment_link_url": action.payment_link_url,
            }
        )

    # --------------------------------------------------
    # Recovery outcome
    # --------------------------------------------------

    if case.amount_recovered > 0:
        events.append(
            {
                "type": "recovery_completed",
                "timestamp": case.updated_at,
                "status": "recovered",
                "title": "Recovery completed",
                "description": (
                    f"{case.amount_recovered} minor currency "
                    f"units recorded as recovered."
                ),
                "amount_recovered": case.amount_recovered,
                "currency": case.currency,
            }
        )

    # --------------------------------------------------
    # Chronological ordering
    # --------------------------------------------------

    events.sort(
        key=lambda event: event["timestamp"]
    )

    return {
        "case_id": case.id,
        "events": events,
        "total": len(events),
    }