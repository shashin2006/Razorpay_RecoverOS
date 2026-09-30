from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recovery_metrics_endpoint():

    response = client.get(
        "/api/ml/recovery-metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_cases" in data
    assert "total_amount_at_risk_minor" in data
    assert "total_amount_recovered_minor" in data
    assert "recovered_cases" in data

    assert "recovery_rate" in data
    assert "amount_recovery_rate" in data

    assert "total_attempts" in data
    assert "executed_actions" in data
    assert "failed_actions" in data

    assert "policy_eligible_cases" in data

    assert "ml_predictions" in data
    assert "ml_outcomes_recorded" in data
    assert "ml_policy_agreement_rate" in data   