import pytest
from pydantic import ValidationError

from backend.schemas import DiagnosisRequest, TelemetryInput


def valid_telemetry():
    return {
        "incident_id": "INC-TEST-001",
        "device_id": "RTR_TEST_1",
        "status": "up",
        "metrics": {
            "latency_ms": 25,
            "packet_loss_pct": 0,
            "jitter_ms": 3,
            "link_utilization_pct": 40,
            "cpu_usage_pct": 30,
            "memory_usage_pct": 50,
            "queue_drops": 0,
            "interface_errors": 0,
        },
        "topology": {"neighbors": ["SW_TEST_1"]},
    }


def test_valid_telemetry_is_accepted():
    telemetry = TelemetryInput(**valid_telemetry())

    assert telemetry.incident_id == "INC-TEST-001"
    assert telemetry.device_id == "RTR_TEST_1"
    assert telemetry.status == "up"


def test_missing_metrics_are_allowed():
    data = valid_telemetry()
    data["metrics"] = {"latency_ms": 25}

    telemetry = TelemetryInput(**data)

    assert telemetry.metrics.latency_ms == 25
    assert telemetry.metrics.packet_loss_pct is None


def test_empty_topology_is_allowed():
    data = valid_telemetry()
    data["topology"] = {}

    telemetry = TelemetryInput(**data)

    assert telemetry.topology == {"neighbors": []}


@pytest.mark.parametrize(
    "metric,value",
    [
        ("latency_ms", -1),
        ("jitter_ms", -1),
        ("queue_drops", -1),
        ("interface_errors", -1),
        ("packet_loss_pct", 101),
        ("packet_loss_pct", -1),
        ("link_utilization_pct", 101),
        ("cpu_usage_pct", 101),
        ("memory_usage_pct", 101),
    ],
)
def test_invalid_metric_values_are_rejected(metric, value):
    data = valid_telemetry()
    data["metrics"][metric] = value

    with pytest.raises(ValidationError):
        TelemetryInput(**data)


@pytest.mark.parametrize("status", ["unknown", "offline", ""])
def test_invalid_device_status_is_rejected(status):
    data = valid_telemetry()
    data["status"] = status

    with pytest.raises(ValidationError):
        TelemetryInput(**data)


@pytest.mark.parametrize("field", ["incident_id", "device_id"])
@pytest.mark.parametrize("value", ["", "   "])
def test_blank_identifiers_are_rejected(field, value):
    data = valid_telemetry()
    data[field] = value

    with pytest.raises(ValidationError):
        TelemetryInput(**data)


def test_identifiers_are_trimmed():
    data = valid_telemetry()
    data["incident_id"] = "  INC-TEST-001  "
    data["device_id"] = "  RTR_TEST_1  "

    telemetry = TelemetryInput(**data)

    assert telemetry.incident_id == "INC-TEST-001"
    assert telemetry.device_id == "RTR_TEST_1"


def test_duplicate_and_blank_neighbors_are_cleaned():
    data = valid_telemetry()
    data["topology"] = {
        "neighbors": [
            " SW_TEST_1 ",
            "",
            "SW_TEST_1",
            "RTR_TEST_2",
        ]
    }

    telemetry = TelemetryInput(**data)

    assert telemetry.topology["neighbors"] == [
        "SW_TEST_1",
        "RTR_TEST_2",
    ]


def test_diagnosis_request_requires_telemetry():
    with pytest.raises(ValidationError):
        DiagnosisRequest()