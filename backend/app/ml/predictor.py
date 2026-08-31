from dataclasses import dataclass

from app.ml.model import (
    load_model,
    predict_recovery_probability,
)


RECOVERY_THRESHOLD = 0.40


@dataclass
class RecoveryPrediction:
    probability: float
    recommends_recovery: bool
    threshold: float


def predict_recovery(
    features: dict,
) -> RecoveryPrediction:

    model = load_model()

    probability = predict_recovery_probability(
        model=model,
        features=features,
    )

    return RecoveryPrediction(
        probability=probability,
        recommends_recovery=(
            probability >= RECOVERY_THRESHOLD
        ),
        threshold=RECOVERY_THRESHOLD,
    )