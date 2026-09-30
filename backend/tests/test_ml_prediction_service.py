from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import MLPrediction
from app.services.ml_prediction_service import (
    record_shadow_prediction,
)


def test_shadow_prediction_is_recorded():

    db = SessionLocal()

    try:

        with patch(
            "app.services.ml_prediction_service.predict_recovery"
        ) as mock_predict:

            mock_predict.return_value.probability = 0.73
            mock_predict.return_value.threshold = 0.40
            mock_predict.return_value.recommends_recovery = True

            result = record_shadow_prediction(
                db=db,
                recovery_case_id=63,
                features={
                    "amount_minor": 50000,
                    "currency": "INR",
                    "payment_method": "netbanking",
                    "failure_category": "bank_decline",
                    "error_source": "bank",
                    "error_step": "payment_authorization",
                    "error_reason": "payment_failed",
                    "error_code": "BAD_REQUEST_ERROR",
                    "attempts": 1,
                    "action_type": "alternate_payment_method",
                    "attempt_number": 1,
                },
            )

        assert result is not None
        assert result.recovery_case_id == 63
        assert result.probability == 0.73
        assert result.threshold == 0.40
        assert result.recommendation is True
        assert result.model_version == "baseline-v1"
        assert result.mode == "shadow"

        saved = (
            db.query(MLPrediction)
            .filter(
                MLPrediction.id == result.id
            )
            .first()
        )

        assert saved is not None
        assert saved.probability == 0.73

    finally:

        if "result" in locals() and result:
            db.delete(result)
            db.commit()

        db.close()