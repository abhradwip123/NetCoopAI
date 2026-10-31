from backend.agents.connectivity_agent import analyze_connectivity


telemetry = {
    "incident_id": "INC-003",
    "device_id": "RTR_CORE_1",
    "status": "down",
    "metrics": {},
    "topology": {
        "neighbors": ["SW_CAMPUS_1", "RTR_CORE_2"]
    },
}

result = analyze_connectivity(telemetry)

print(result.model_dump_json(indent=2))