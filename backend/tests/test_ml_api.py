from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ml_evaluation_endpoint():

    response = client.get(
        "/api/ml/evaluation"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_predictions" in data
    assert "recovered_predictions" in data
    assert "unrecovered_predictions" in data
    assert "recovery_rate" in data
    assert "total_revenue_recovered" in data
    assert "accuracy" in data
    assert "precision" in data
    assert "recall" in data
    assert "f1" in data
    assert "roc_auc" in data


def test_probability_buckets_endpoint():

    response = client.get(
        "/api/ml/probability-buckets"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert len(data) == 6

    assert data[0]["bucket"] == "0.40-0.50"
    assert data[1]["bucket"] == "0.50-0.60"
    assert data[2]["bucket"] == "0.60-0.70"
    assert data[3]["bucket"] == "0.70-0.80"
    assert data[4]["bucket"] == "0.80-0.90"
    assert data[5]["bucket"] == "0.90-1.01"

    for bucket in data:

        assert "bucket" in bucket
        assert "predictions" in bucket
        assert "recovered" in bucket
        assert "recovery_rate" in bucket
        assert "revenue_recovered" in bucket


def test_decision_agreement_endpoint():

    response = client.get(
        "/api/ml/decision-agreement"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_decisions" in data
    assert "agreements" in data
    assert "disagreements" in data
    assert "agreement_rate" in data

def test_ml_dashboard_endpoint():

    response = client.get(
        "/api/ml/dashboard"
    )

    assert response.status_code == 200

    data = response.json()

    assert "evaluation" in data
    assert "probability_buckets" in data
    assert "decision_agreement" in data

    evaluation = data["evaluation"]

    assert "total_predictions" in evaluation
    assert "recovered_predictions" in evaluation
    assert "unrecovered_predictions" in evaluation
    assert "recovery_rate" in evaluation
    assert "total_revenue_recovered" in evaluation

    buckets = data["probability_buckets"]

    assert isinstance(buckets, list)
    assert len(buckets) == 6

    agreement = data["decision_agreement"]

    assert "total_decisions" in agreement
    assert "agreements" in agreement
    assert "disagreements" in agreement
    assert "agreement_rate" in agreement