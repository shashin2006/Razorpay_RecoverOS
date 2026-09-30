from sqlalchemy.orm import Session

from app.db.models import MLPrediction


def record_recovery_outcome(
    db: Session,
    recovery_case_id: int,
    amount_recovered: int,
):
    prediction = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.recovery_case_id
            == recovery_case_id,
            MLPrediction.mode == "shadow",
            MLPrediction.outcome_recorded == False,
        )
        .order_by(
            MLPrediction.id.desc()
        )
        .first()
    )

    if prediction is None:
        return None

    prediction.actual_recovered = (
        amount_recovered
    )

    prediction.outcome_recorded = True

    db.commit()
    db.refresh(prediction)

    return prediction