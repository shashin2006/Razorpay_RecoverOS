from unittest.mock import patch

from app.ml.predictor import (
    RecoveryPrediction,
    predict_recovery,
)


def test_high_probability_recommends_recovery():

    with patch(
        "app.ml.predictor.predict_recovery_probability",
        return_value=0.75,
    ):

        result = predict_recovery(
            features={}
        )

    assert isinstance(
        result,
        RecoveryPrediction,
    )

    assert result.probability == 0.75
    assert result.threshold == 0.40
    assert result.recommends_recovery is True


def test_low_probability_does_not_recommend_recovery():

    with patch(
        "app.ml.predictor.predict_recovery_probability",
        return_value=0.25,
    ):

        result = predict_recovery(
            features={}
        )

    assert result.probability == 0.25
    assert result.threshold == 0.40
    assert result.recommends_recovery is False


def test_threshold_probability_recommends_recovery():

    with patch(
        "app.ml.predictor.predict_recovery_probability",
        return_value=0.40,
    ):

        result = predict_recovery(
            features={}
        )

    assert result.recommends_recovery is True