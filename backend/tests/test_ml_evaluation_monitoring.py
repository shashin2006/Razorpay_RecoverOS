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
    db_session,
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
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(prediction)
    db_session.commit()
    db_session.refresh(prediction)

    try:
        result = get_ml_evaluation(db_session)

        assert result["total_predictions"] >= 1
        assert result["recovered_predictions"] >= 1
        assert result["recovery_rate"] > 0
        assert result["total_revenue_recovered"] >= 50000

    finally:
        db_session.delete(prediction)
        db_session.commit()