from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
    RecoveryAction,
    RecoveryCase,
)


@dataclass
class RecoveryMetrics:
    total_cases: int
    total_amount_at_risk_minor: int
    total_amount_recovered_minor: int
    recovered_cases: int
    recovery_rate: float
    amount_recovery_rate: float
    total_attempts: int
    executed_actions: int
    failed_actions: int
    policy_eligible_cases: int
    ml_predictions: int
    ml_outcomes_recorded: int
    ml_policy_agreement_rate: float


def calculate_recovery_metrics(
    db: Session,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> RecoveryMetrics:

    case_query = db.query(RecoveryCase)

    if start_time is not None:
        case_query = case_query.filter(
            RecoveryCase.created_at >= start_time
        )

    if end_time is not None:
        case_query = case_query.filter(
            RecoveryCase.created_at < end_time
        )

    cases = case_query.all()

    case_ids = [case.id for case in cases]

    total_cases = len(cases)

    total_amount_at_risk = sum(
        case.amount_at_risk_minor
        for case in cases
    )

    total_amount_recovered = sum(
        case.amount_recovered
        for case in cases
    )

    recovered_cases = sum(
        1
        for case in cases
        if case.status == "recovered"
    )

    recovery_rate = (
        recovered_cases / total_cases
        if total_cases > 0
        else 0.0
    )

    amount_recovery_rate = (
        total_amount_recovered / total_amount_at_risk
        if total_amount_at_risk > 0
        else 0.0
    )

    total_attempts = sum(
        case.attempts
        for case in cases
    )

    if case_ids:
        executed_actions = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id.in_(case_ids),
                RecoveryAction.status == "executed",
            )
            .count()
        )

        failed_actions = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id.in_(case_ids),
                RecoveryAction.status == "failed",
            )
            .count()
        )

        policy_eligible_cases = (
            db.query(MLDecisionAudit)
            .filter(
                MLDecisionAudit.recovery_case_id.in_(case_ids),
                MLDecisionAudit.policy_eligible.is_(True),
            )
            .count()
        )

        ml_predictions = (
            db.query(MLPrediction)
            .filter(
                MLPrediction.recovery_case_id.in_(case_ids)
            )
            .count()
        )

        ml_outcomes_recorded = (
            db.query(MLPrediction)
            .filter(
                MLPrediction.recovery_case_id.in_(case_ids),
                MLPrediction.outcome_recorded.is_(True),
            )
            .count()
        )

        total_audits = (
            db.query(MLDecisionAudit)
            .filter(
                MLDecisionAudit.recovery_case_id.in_(case_ids)
            )
            .count()
        )

        agreement_count = (
            db.query(MLDecisionAudit)
            .filter(
                MLDecisionAudit.recovery_case_id.in_(case_ids),
                MLDecisionAudit.agreement.is_(True),
            )
            .count()
        )

    else:
        executed_actions = 0
        failed_actions = 0
        policy_eligible_cases = 0
        ml_predictions = 0
        ml_outcomes_recorded = 0
        total_audits = 0
        agreement_count = 0

    ml_policy_agreement_rate = (
        agreement_count / total_audits
        if total_audits > 0
        else 0.0
    )

    return RecoveryMetrics(
        total_cases=total_cases,
        total_amount_at_risk_minor=total_amount_at_risk,
        total_amount_recovered_minor=total_amount_recovered,
        recovered_cases=recovered_cases,
        recovery_rate=recovery_rate,
        amount_recovery_rate=amount_recovery_rate,
        total_attempts=total_attempts,
        executed_actions=executed_actions,
        failed_actions=failed_actions,
        policy_eligible_cases=policy_eligible_cases,
        ml_predictions=ml_predictions,
        ml_outcomes_recorded=ml_outcomes_recorded,
        ml_policy_agreement_rate=ml_policy_agreement_rate,
    )