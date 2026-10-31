import pytest
from pydantic import ValidationError

from backend.schemas import TelemetryInput


def valid_telemetry():
    return {
        "incident_id": "INC-001",
        "device_id": "RTR_CORE_1",
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
        "topology": {
            "neighbors": ["SW_CAMPUS_1", "RTR_CORE_2"]
        },
    }


def test_valid_telemetry_is_accepted():
    telemetry = TelemetryInput(**valid_telemetry())
    assert telemetry.device_id == "RTR_CORE_1"


@pytest.mark.parametrize(
    "field,value",
    [
        ("latency_ms", -1),
        ("packet_loss_pct", 101),
        ("link_utilization_pct", 101),
        ("cpu_usage_pct", -1),
        ("memory_usage_pct", 101),
        ("queue_drops", -1),
        ("interface_errors", -1),
    ],
)
def test_invalid_metric_values_are_rejected(field, value):
    data = valid_telemetry()
    data["metrics"][field] = value

    with pytest.raises(ValidationError):
        TelemetryInput(**data)


def test_blank_device_id_is_rejected():
    data = valid_telemetry()
    data["device_id"] = "   "

    with pytest.raises(ValidationError):
        TelemetryInput(**data)


def test_duplicate_neighbors_are_removed():
    data = valid_telemetry()
    data["topology"]["neighbors"] = [
        "SW_CAMPUS_1",
        " SW_CAMPUS_1 ",
        "RTR_CORE_2",
    ]

    telemetry = TelemetryInput(**data)

    assert telemetry.topology["neighbors"] == [
        "SW_CAMPUS_1",
        "RTR_CORE_2",
    ]