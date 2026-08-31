from app.db.database import SessionLocal
from app.db.models import MLPrediction
from app.services.ml_outcome_service import (
    record_recovery_outcome,
)


def test_recovery_outcome_is_recorded():

    db = SessionLocal()

    prediction = MLPrediction(
        recovery_case_id=999991,
        probability=0.6916,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        actual_recovered=None,
        outcome_recorded=False,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    try:

        result = record_recovery_outcome(
            db=db,
            recovery_case_id=999991,
            amount_recovered=50000,
        )

        assert result is not None
        assert result.actual_recovered == 50000
        assert result.outcome_recorded is True

    finally:

        db.delete(prediction)
        db.commit()
        db.close()


def test_recording_outcome_is_idempotent():

    db = SessionLocal()

    prediction = MLPrediction(
        recovery_case_id=999992,
        probability=0.6916,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        actual_recovered=None,
        outcome_recorded=False,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    try:

        first = record_recovery_outcome(
            db=db,
            recovery_case_id=999992,
            amount_recovered=50000,
        )

        assert first.actual_recovered == 50000
        assert first.outcome_recorded is True

        second = record_recovery_outcome(
            db=db,
            recovery_case_id=999992,
            amount_recovered=25000,
        )

        assert second is None

    finally:

        db.delete(prediction)
        db.commit()
        db.close()  