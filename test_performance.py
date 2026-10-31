
from backend.agents.performance_agent import analyze_performance


telemetry = {
    "incident_id": "INC-001",
    "device_id": "SW_CAMPUS_1",
    "metrics": {
        "latency_ms": 280,
        "packet_loss_pct": 5,
        "jitter_ms": 45,
        "link_utilization_pct": 94,
    },
}

result = analyze_performance(telemetry)

print(result.model_dump_json(indent=2))
