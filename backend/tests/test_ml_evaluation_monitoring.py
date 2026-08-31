from datetime import datetime, timezone

from app.db.models import (
    MLDecisionAudit,
    MLPrediction,
)
from app.services.ml_evaluation import (
    get_ml_evaluation,
    get_policy_ml_agreement,
)


def test_ml_evaluation_with_completed_prediction(
    db,
):
    prediction = MLPrediction(
        recovery_case_id=9991,
        probability=0.75,
        threshold=0.40,
        recommendation=True,
        actual_recovered=50000,
        outcome_recorded=True,
        model_version="test-v1",
        mode="shadow",
        created_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(prediction)
    db.commit()

    result = get_ml_evaluation(db)

    assert result["total_predictions"] >= 1
    assert result["recovered_predictions"] >= 1
    assert result["total_revenue_recovered"] >= 50000


def test_policy_ml_agreement(db):

    audit = MLDecisionAudit(
        recovery_case_id=9992,
        policy_eligible=True,
        policy_action=(
            "alternate_payment_method"
        ),
        ml_probability=0.75,
        ml_threshold=0.40,
        ml_recommendation=True,
        agreement=True,
        created_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(audit)
    db.commit()

    result = get_policy_ml_agreement(db)

    assert result["total_decisions"] >= 1
    assert result["agreements"] >= 1