from sqlalchemy.orm import Session

from app.db.models import MLPrediction
from app.ml.predictor import predict_recovery


MODEL_VERSION = "baseline-v1"
MODE = "shadow"


def record_shadow_prediction(
    db: Session,
    recovery_case_id: int,
    features: dict,
):
    prediction = predict_recovery(
        features=features,
    )

    record = MLPrediction(
        recovery_case_id=recovery_case_id,
        probability=prediction.probability,
        threshold=prediction.threshold,
        recommendation=prediction.recommends_recovery,
        model_version=MODEL_VERSION,
        mode=MODE,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record