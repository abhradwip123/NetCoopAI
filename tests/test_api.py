
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def valid_payload():
    return {
        "telemetry": {
            "incident_id": "API-TEST-001",
            "device_id": "RTR_1",
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
            "topology": {"neighbors": ["SW_1"]},
        }
    }


def test_diagnose_endpoint_returns_congestion_report(client):
    response = client.post("/api/diagnose", json=valid_payload())

    assert response.status_code == 200

    report = response.json()
    assert report["incident_id"] == "API-TEST-001"
    assert report["root_cause"] == "congestion"
    assert report["recommended_actions"]
    assert "RTR_1" in report["affected_devices"]


def test_diagnose_endpoint_rejects_invalid_metric(client):
    payload = valid_payload()
    payload["telemetry"]["metrics"]["latency_ms"] = -10

    response = client.post("/api/diagnose", json=payload)

    assert response.status_code == 422


def test_diagnose_endpoint_rejects_non_numeric_metric(client):
    payload = valid_payload()
    payload["telemetry"]["metrics"]["latency_ms"] = "not-a-number"

    response = client.post("/api/diagnose", json=payload)

    assert response.status_code == 422


def test_diagnose_endpoint_rejects_missing_device_id(client):
    payload = valid_payload()
    del payload["telemetry"]["device_id"]

    response = client.post("/api/diagnose", json=payload)

    assert response.status_code == 422


def test_diagnose_endpoint_rejects_invalid_status(client):
    payload = valid_payload()
    payload["telemetry"]["status"] = "offline"

    response = client.post("/api/diagnose", json=payload)

    assert response.status_code == 422


def test_diagnose_endpoint_rejects_blank_incident_id(client):
    payload = valid_payload()
    payload["telemetry"]["incident_id"] = "   "

    response = client.post("/api/diagnose", json=payload)

    assert response.status_code == 422


def test_diagnose_endpoint_rejects_missing_request_body(client):
    response = client.post("/api/diagnose")

    assert response.status_code == 422
