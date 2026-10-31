from backend.agents.performance_agent import analyze_performance
from backend.agents.infrastructure_agent import analyze_infrastructure
from backend.agents.connectivity_agent import analyze_connectivity
from backend.agents.correlation_agent import correlate_findings


telemetry = {
    "incident_id": "INC-004",
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

messages = [
    analyze_performance(telemetry),
    analyze_infrastructure(telemetry),
    analyze_connectivity(telemetry),
]

report = correlate_findings(messages)

import json
print(json.dumps(report, indent=2))