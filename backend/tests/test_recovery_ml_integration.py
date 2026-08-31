from unittest.mock import patch

from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryAction, RecoveryCase
from app.ml.features import build_recovery_features
from app.ml.predictor import predict_recovery


def test_recovery_prediction_from_real_entities():

    db = SessionLocal()

    payment_id = "pay_ml_integration_test_001"

    payment = Payment(
        razorpay_payment_id=payment_id,
        razorpay_order_id="order_ml_integration_test_001",
        amount_minor=50000,
        currency="INR",
        method="netbanking",
        status="failed",
        error_code="BAD_REQUEST_ERROR",
        error_step="payment_authorization",
        error_reason="payment_failed",
        error_source="bank",
        error_description="Bank declined payment.",
        created_at=__import__(
            "datetime"
        ).datetime.now(
            __import__(
                "datetime"
            ).timezone.utc
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    case = RecoveryCase(
        payment_id=payment_id,
        amount_at_risk_minor=50000,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=1,
        amount_recovered=0,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    action = RecoveryAction(
        recovery_case_id=case.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Bank declined payment.",
        external_id="plink_ml_integration_test_001",
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    try:

        features = build_recovery_features(
            payment=payment,
            recovery_case=case,
            recovery_action=action,
        )

        assert features is not None
        assert isinstance(features, dict)

        with patch(
            "app.ml.predictor.predict_recovery_probability",
            return_value=0.75,
        ):

            prediction = predict_recovery(
                features=features
            )

        assert prediction.probability == 0.75
        assert prediction.threshold == 0.40
        assert prediction.recommends_recovery is True

    finally:

        db.delete(action)
        db.delete(case)
        db.delete(payment)

        db.commit()
        db.close()