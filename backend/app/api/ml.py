from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.ml_evaluation import (
    get_ml_evaluation,
    get_probability_bucket_analysis,
    get_policy_ml_agreement,
)
from app.services.recovery_metrics import calculate_recovery_metrics


router = APIRouter(
    prefix="/api/ml",
    tags=["ML Monitoring"],
)


@router.get("/evaluation")
def ml_evaluation(
    db: Session = Depends(get_db),
):
    return get_ml_evaluation(db)


@router.get("/probability-buckets")
def probability_buckets(
    db: Session = Depends(get_db),
):
    return get_probability_bucket_analysis(db)


@router.get("/decision-agreement")
def decision_agreement(
    db: Session = Depends(get_db),
):
    return get_policy_ml_agreement(db)


@router.get("/recovery-metrics")
def recovery_metrics(
    db: Session = Depends(get_db),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
):
    """
    Return measurable revenue recovery metrics.

    Optional start_time and end_time parameters allow
    metrics to be calculated for a specific recovery batch
    or reporting window.
    """

    metrics = calculate_recovery_metrics(
        db=db,
        start_time=start_time,
        end_time=end_time,
    )

    return {
        "total_cases": metrics.total_cases,
        "total_amount_at_risk_minor": (
            metrics.total_amount_at_risk_minor
        ),
        "total_amount_recovered_minor": (
            metrics.total_amount_recovered_minor
        ),
        "recovered_cases": metrics.recovered_cases,
        "recovery_rate": metrics.recovery_rate,
        "amount_recovery_rate": metrics.amount_recovery_rate,
        "total_attempts": metrics.total_attempts,
        "executed_actions": metrics.executed_actions,
        "failed_actions": metrics.failed_actions,
        "policy_eligible_cases": (
            metrics.policy_eligible_cases
        ),
        "ml_predictions": metrics.ml_predictions,
        "ml_outcomes_recorded": (
            metrics.ml_outcomes_recorded
        ),
        "ml_policy_agreement_rate": (
            metrics.ml_policy_agreement_rate
        ),
    }


@router.get("/dashboard")
def ml_dashboard(
    db: Session = Depends(get_db),
):
    """
    Return consolidated ML monitoring information
    for the RecoveryOS dashboard.
    """

    return {
        "evaluation": get_ml_evaluation(db),
        "probability_buckets": (
            get_probability_bucket_analysis(db)
        ),
        "decision_agreement": (
            get_policy_ml_agreement(db)
        ),
    }