from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.services.ml_evaluation import (
    get_ml_evaluation,
    get_probability_bucket_analysis,
    get_policy_ml_agreement,
)


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