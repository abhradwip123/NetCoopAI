import json

from backend.schemas import TelemetryInput
from backend.agents.performance_agent import analyze_performance
from backend.agents.infrastructure_agent import analyze_infrastructure
from backend.agents.connectivity_agent import analyze_connectivity
from backend.agents.correlation_agent import correlate_findings
from backend.agents.reporting_agent import create_incident_report


telemetry = TelemetryInput(
    incident_id="INC-005",
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

telemetry_dict = telemetry.model_dump()

messages = [
    analyze_performance(telemetry_dict),
    analyze_infrastructure(telemetry_dict),
    analyze_connectivity(telemetry_dict),
]

diagnosis = correlate_findings(messages)
report = create_incident_report(telemetry, diagnosis)

print(json.dumps(report, indent=2))