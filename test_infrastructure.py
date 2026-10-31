from backend.agents.infrastructure_agent import analyze_infrastructure


telemetry = {
    "incident_id": "INC-002",
    "device_id": "SW_CAMPUS_1",
    "metrics": {
        "cpu_usage_pct": 96,
        "memory_usage_pct": 72,
        "queue_drops": 250,
        "interface_errors": 80,
    },
}

result = analyze_infrastructure(telemetry)

print(result.model_dump_json(indent=2))