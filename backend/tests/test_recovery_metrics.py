from datetime import datetime, timedelta, timezone

from app.db.models import (
    MLPrediction,
    MLDecisionAudit,
    RecoveryAction,
    RecoveryCase,
)
from app.services.recovery_metrics import calculate_recovery_metrics


def test_recovery_metrics_calculate_batch_totals(db_session):

    now = datetime.now(timezone.utc)

    # Use unique IDs for this test run.
    run_id = now.strftime("%Y%m%d%H%M%S%f")

    payment_id_1 = f"metrics_payment_batch_001_{run_id}"
    payment_id_2 = f"metrics_payment_batch_002_{run_id}"
    external_id = f"plink_metrics_batch_001_{run_id}"

    case_1 = RecoveryCase(
        payment_id=payment_id_1,
        amount_at_risk_minor=50000,
        amount_recovered=50000,
        currency="INR",
        failure_category="bank_decline",
        status="recovered",
        attempts=1,
        created_at=now,
        updated_at=now,
    )

    case_2 = RecoveryCase(
        payment_id=payment_id_2,
        amount_at_risk_minor=30000,
        amount_recovered=0,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=1,
        created_at=now,
        updated_at=now,
    )

    db_session.add_all([case_1, case_2])
    db_session.commit()

    action = RecoveryAction(
        recovery_case_id=case_1.id,
        action_type="alternate_payment_method",
        status="executed",
        attempt_number=1,
        reason="Bank authorization decline is recoverable.",
        external_id=external_id,
        created_at=now,
        executed_at=now,
    )

    prediction_1 = MLPrediction(
        recovery_case_id=case_1.id,
        probability=0.80,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        actual_recovered=50000,
        outcome_recorded=True,
    )

    prediction_2 = MLPrediction(
        recovery_case_id=case_2.id,
        probability=0.70,
        threshold=0.40,
        recommendation=True,
        model_version="baseline-v1",
        mode="shadow",
        outcome_recorded=False,
    )

    audit_1 = MLDecisionAudit(
        recovery_case_id=case_1.id,
        policy_eligible=True,
        policy_action="alternate_payment_method",
        ml_probability=0.80,
        ml_threshold=0.40,
        ml_recommendation=True,
        agreement=True,
        created_at=now,
    )

    audit_2 = MLDecisionAudit(
        recovery_case_id=case_2.id,
        policy_eligible=True,
        policy_action="alternate_payment_method",
        ml_probability=0.70,
        ml_threshold=0.40,
        ml_recommendation=True,
        agreement=True,
        created_at=now,
    )

    db_session.add_all(
        [
            action,
            prediction_1,
            prediction_2,
            audit_1,
            audit_2,
        ]
    )
    db_session.commit()

    metrics = calculate_recovery_metrics(
        db_session,
        start_time=now - timedelta(seconds=1),
        end_time=now + timedelta(seconds=1),
    )

    assert metrics.total_cases == 2
    assert metrics.total_amount_at_risk_minor == 80000
    assert metrics.total_amount_recovered_minor == 50000

    assert metrics.recovered_cases == 1
    assert metrics.recovery_rate == 0.5
    assert metrics.amount_recovery_rate == 0.625

    assert metrics.total_attempts == 2
    assert metrics.executed_actions == 1
    assert metrics.failed_actions == 0

    assert metrics.policy_eligible_cases == 2

    assert metrics.ml_predictions == 2
    assert metrics.ml_outcomes_recorded == 1

    assert metrics.ml_policy_agreement_rate == 1.0

    # Clean up all rows created by this test.
    db_session.delete(audit_1)
    db_session.delete(audit_2)
    db_session.delete(prediction_1)
    db_session.delete(prediction_2)
    db_session.delete(action)
    db_session.delete(case_1)
    db_session.delete(case_2)

    db_session.commit()