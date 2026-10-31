
import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def valid_payload(incident_id="HISTORY-TEST-001"):
    return {
        "telemetry": {
            "incident_id": incident_id,
            "device_id": "RTR_HISTORY",
            "status": "up",
            "metrics": {
                "latency_ms": 280,
                "packet_loss_pct": 5,
                "jitter_ms": 45,
                "link_utilization_pct": 94,
                "cpu_usage_pct": 96,
                "memory_usage_pct": 72,
                "queue_drops": 250,
                "interface_errors": 80,
            },
            "topology": {"neighbors": ["SW_HISTORY"]},
        }
    }


def test_diagnosis_is_saved_and_appears_in_history():
    diagnosis_response = client.post(
        "/api/diagnose",
        json=valid_payload(),
    )
    assert diagnosis_response.status_code == 200

    history_response = client.get("/api/history")
    assert history_response.status_code == 200

    records = history_response.json()
    matching_records = [
        record
        for record in records
        if record["incident_id"] == "HISTORY-TEST-001"
    ]

    assert matching_records
    record = matching_records[0]
    assert record["device_id"] == "RTR_HISTORY"
    assert record["root_cause"] == diagnosis_response.json()["root_cause"]
    assert record["severity"] == diagnosis_response.json()["severity"]
    assert "id" in record
    assert "created_at" in record


def test_history_record_returns_full_saved_report():
    diagnosis_response = client.post(
        "/api/diagnose",
        json=valid_payload("HISTORY-TEST-002"),
    )
    assert diagnosis_response.status_code == 200

    history_response = client.get("/api/history")
    records = history_response.json()

    record = next(
        item
        for item in records
        if item["incident_id"] == "HISTORY-TEST-002"
    )

    detail_response = client.get(f"/api/history/{record['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json() == diagnosis_response.json()


def test_history_record_returns_404_for_unknown_id():
    response = client.get("/api/history/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Diagnosis history record not found"


@pytest.mark.parametrize("limit", [0, -1, 201])
def test_history_rejects_invalid_limit(limit):
    response = client.get("/api/history", params={"limit": limit})

    assert response.status_code == 400
    assert response.json()["detail"] == "limit must be between 1 and 200"


def test_history_accepts_valid_limit():
    response = client.get("/api/history", params={"limit": 1})

    assert response.status_code == 200
    assert isinstance(response.json(), list)
