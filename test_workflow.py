import json

from backend.schemas import TelemetryInput
from backend.orchestration.workflow import run_diagnosis


telemetry = TelemetryInput(
    incident_id="INC-006",
    device_id="RTR_CORE_1",
    status="up",
    metrics={
        "latency_ms": 280,
        "packet_loss_pct": 5,
        "jitter_ms": 45,
        "link_utilization_pct": 94,
        "cpu_usage_pct": 96,
        "memory_usage_pct": 72,
        "queue_drops": 250,
        "interface_errors": 80,
    },
    topology={
        "neighbors": ["SW_CAMPUS_1", "RTR_CORE_2"]
    },
)

report = run_diagnosis(telemetry)

print(json.dumps(report, indent=2))