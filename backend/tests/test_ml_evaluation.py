from app.db.database import SessionLocal
from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
)
from app.services.ml_evaluation import (
    get_ml_evaluation,
    get_probability_bucket_analysis,
    get_policy_ml_agreement,
)


def test_ml_evaluation_counts_recovered_outcomes():

    db = SessionLocal()

    prediction = MLPrediction(
        recovery_case_id=999901,
        probability=0.80,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        actual_recovered=50000,
        outcome_recorded=True,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    try:

        result = get_ml_evaluation(db)

        assert result["total_predictions"] >= 1
        assert result["recovered_predictions"] >= 1
        assert result["recovery_rate"] > 0
        assert result["total_revenue_recovered"] >= 50000

    finally:

        db.delete(prediction)
        db.commit()
        db.close()

def test_probability_bucket_analysis():

    db = SessionLocal()

    predictions = [
        MLPrediction(
            recovery_case_id=999902,
            probability=0.45,
            threshold=0.40,
            recommendation=True,
            model_version="baseline-v1",
            mode="shadow",
            actual_recovered=50000,
            outcome_recorded=True,
        ),
        MLPrediction(
            recovery_case_id=999903,
            probability=0.65,
            threshold=0.40,
            recommendation=True,
            model_version="baseline-v1",
            mode="shadow",
            actual_recovered=50000,
            outcome_recorded=True,
        ),
        MLPrediction(
            recovery_case_id=999904,
            probability=0.65,
            threshold=0.40,
            recommendation=True,
            model_version="baseline-v1",
            mode="shadow",
            actual_recovered=0,
            outcome_recorded=True,
        ),
    ]

    db.add_all(predictions)
    db.commit()

    try:

        result = get_probability_bucket_analysis(db)

        buckets = {
            item["bucket"]: item
            for item in result
        }

        assert buckets["0.40-0.50"]["predictions"] >= 1

        assert buckets["0.60-0.70"]["predictions"] >= 2

        assert (
            buckets["0.60-0.70"]["recovery_rate"]
            < 1.0
        )

    finally:

        for prediction in predictions:
            db.delete(prediction)

        db.commit()
        db.close()

def test_policy_ml_agreement():

    db = SessionLocal()

    audit = MLDecisionAudit(
        recovery_case_id=999905,
        policy_eligible=True,
        policy_action="alternate_payment_method",
        ml_probability=0.75,
        ml_threshold=0.40,
        ml_recommendation=True,
        agreement=True,
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    try:

        result = get_policy_ml_agreement(db)

        assert result["total_decisions"] >= 1
        assert result["agreements"] >= 1
        assert result["agreement_rate"] > 0

    finally:

        db.delete(audit)
        db.commit()
        db.close()