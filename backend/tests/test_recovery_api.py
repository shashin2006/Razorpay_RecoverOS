from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recovery_cases_endpoint_returns_success():
    response = client.get("/api/recovery/cases")

    assert response.status_code == 200

    data = response.json()

    assert "cases" in data
    assert "total" in data
    assert isinstance(data["cases"], list)
    assert isinstance(data["total"], int)


def test_recovery_case_not_found():
    response = client.get("/api/recovery/cases/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recovery case not found."

def test_recovery_case_audit_not_found():
    response = client.get(
        "/api/recovery/cases/999999999/audit"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Recovery case not found."

def test_recovery_case_audit_returns_events():
    cases_response = client.get(
        "/api/recovery/cases"
    )

    assert cases_response.status_code == 200

    cases = cases_response.json()["cases"]

    if not cases:
        return

    case_id = cases[0]["id"]

    response = client.get(
        f"/api/recovery/cases/{case_id}/audit"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case_id
    assert "events" in data
    assert "total" in data
    assert isinstance(data["events"], list)
    assert isinstance(data["total"], int)

    for event in data["events"]:
        assert "type" in event
        assert "timestamp" in event
        assert "status" in event
        assert "title" in event
        assert "description" in event