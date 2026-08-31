from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
    Payment,
    RecoveryAction,
    RecoveryCase,
)
from app.ml.features import build_recovery_features
from app.services.ml_prediction_service import (
    record_shadow_prediction,
)
from app.services.recovery_policy import (
    determine_recovery_action,
)


@dataclass
class MLDecisionComparison:
    policy_eligible: bool
    policy_action: str
    ml_probability: float
    ml_recommendation: bool
    threshold: float
    agreement: bool


def evaluate_ml_against_policy(
    db: Session,
    payment: Payment,
    recovery_case: RecoveryCase,
    recovery_action: RecoveryAction | None = None,
) -> MLDecisionComparison:

    # ----------------------------------------
    # POLICY DECISION
    # ----------------------------------------

    policy_decision = determine_recovery_action(
        recovery_case=recovery_case,
    )

    # ----------------------------------------
    # BUILD ML FEATURES
    # ----------------------------------------

    features = build_recovery_features(
        payment=payment,
        recovery_case=recovery_case,
        recovery_action=recovery_action,
    )

    # ----------------------------------------
    # RECORD ML SHADOW PREDICTION
    # ----------------------------------------

    prediction = record_shadow_prediction(
        db=db,
        recovery_case_id=recovery_case.id,
        features=features,
    )

    # ----------------------------------------
    # COMPARE POLICY AND ML
    # ----------------------------------------

    policy_recommends = (
        policy_decision.eligible
    )

    ml_recommends = (
        prediction.recommendation
    )

    agreement = (
        policy_recommends
        == ml_recommends
    )

    # ----------------------------------------
    # RECORD DECISION AUDIT
    # ----------------------------------------

    audit = MLDecisionAudit(
        recovery_case_id=recovery_case.id,
        policy_eligible=policy_recommends,
        policy_action=policy_decision.action.value,
        ml_probability=prediction.probability,
        ml_threshold=prediction.threshold,
        ml_recommendation=ml_recommends,
        agreement=agreement,
    )

    db.add(audit)
    db.commit()

    return MLDecisionComparison(
        policy_eligible=policy_recommends,
        policy_action=policy_decision.action.value,
        ml_probability=prediction.probability,
        ml_recommendation=ml_recommends,
        threshold=prediction.threshold,
        agreement=agreement,
    )