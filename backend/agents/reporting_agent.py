
from backend.schemas import TelemetryInput


ACTIONS_BY_CAUSE = {
    "device_unreachable": [
        "Verify device power, management connectivity, and interface status.",
        "Check recent configuration changes and device logs.",
    ],
    "device_degraded": [
        "Inspect device health and recent system logs.",
        "Check resource utilization and recent configuration changes.",
    ],
    "congestion": [
        "Inspect traffic patterns and identify high-volume flows.",
        "Consider traffic shaping or increasing link capacity.",
    ],
    "interface_queue_congestion": [
        "Inspect interface queue statistics and congestion drops.",
        "Review QoS policies and traffic bursts.",
    ],
    "packet_loss": [
        "Check interface counters and end-to-end packet loss.",
        "Inspect routing paths and physical link health.",
    ],
    "latency_degradation": [
        "Measure latency across the path to isolate the affected segment.",
        "Inspect congestion, routing changes, and device load.",
    ],
    "jitter": [
        "Inspect queueing and congestion along the traffic path.",
        "Review QoS settings for delay-sensitive traffic.",
    ],
    "device_cpu_overload": [
        "Identify processes consuming CPU and inspect control-plane load.",
        "Check for abnormal traffic or recent configuration changes.",
    ],
    "device_memory_pressure": [
        "Inspect memory-consuming processes and system logs.",
        "Check for memory leaks or resource exhaustion.",
    ],
    "interface_errors": [
        "Inspect physical cabling, optics, and interface counters.",
        "Check for duplex, speed, or hardware issues.",
    ],
}


def _valid_dict_items(items: object) -> list[dict]:
    """Return only dictionary entries from a list-like value."""
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def determine_severity(root_cause: str, confidence: float) -> str:
    """Assign incident severity based on root cause."""

    if root_cause == "device_unreachable":
        return "Critical"

    if root_cause in {
        "congestion",
        "interface_queue_congestion",
        "device_cpu_overload",
    }:
        return "High"

    if root_cause in {
        "packet_loss",
        "latency_degradation",
        "jitter",
        "device_memory_pressure",
        "interface_errors",
        "device_degraded",
    }:
        return "Medium"

    return "Low"


def create_incident_report(
    telemetry: TelemetryInput,
    diagnosis: dict,
) -> dict:
    """Build a structured incident report matching the required output."""

    device_id = telemetry.device_id
    root_cause = diagnosis.get("root_cause") or "undetermined"
    confidence = diagnosis.get("confidence", 0.0)

    ranked_causes = _valid_dict_items(diagnosis.get("ranked_causes", []))
    evidence = _valid_dict_items(diagnosis.get("evidence", []))

    alternative_items = [
        item
        for item in ranked_causes
        if isinstance(item.get("cause"), str)
        and item["cause"] != root_cause
    ]

    alternatives = [item["cause"] for item in alternative_items]

    ranked_alternative_causes = [
        {
            "rank": rank,
            "cause": item["cause"],
            "score": item.get("score", 0.0),
            "supporting_metrics": item.get("evidence_metrics", []),
        }
        for rank, item in enumerate(alternative_items, start=1)
    ]

    affected_devices = [device_id]
    neighbors = telemetry.topology.get("neighbors", [])

    if isinstance(neighbors, list):
        for neighbor in neighbors:
            if (
                isinstance(neighbor, str)
                and neighbor.strip()
                and neighbor not in affected_devices
            ):
                affected_devices.append(neighbor)

    evidence_sources = sorted({
        item.get("agent_id", "unknown")
        for item in evidence
        if isinstance(item.get("agent_id", "unknown"), str)
    })

    supporting_evidence = [
        {
            "metric": item.get("metric", "unknown"),
            "value": item.get("value"),
            "interpretation": item.get("interpretation", ""),
        }
        for item in evidence
    ]

    recommended_actions = ACTIONS_BY_CAUSE.get(
        root_cause,
        ["Collect additional telemetry and inspect device logs."],
    )

    limitations = diagnosis.get("limitations", [])
    if not isinstance(limitations, list):
        limitations = []

    if root_cause == "undetermined" and not limitations:
        limitations = ["Insufficient evidence for a reliable diagnosis."]

    # Required output fields.
    required_report = {
        "incident_id": telemetry.incident_id,
        "status": (
            "diagnosed"
            if root_cause != "undetermined"
            else "insufficient_evidence"
        ),
        "suspected_root_cause": diagnosis.get(
            "root_cause_explanation",
            root_cause,
        ),
        "confidence": confidence,
        "affected_devices": affected_devices,
        "supporting_evidence": supporting_evidence,
        "alternative_causes": alternatives,
        "ranked_alternative_causes": ranked_alternative_causes,
        "recommended_actions": recommended_actions,
        "evidence_sources": evidence_sources,
        "limitations": limitations,
    }

    # Preserve existing fields for dashboard and test compatibility.
    required_report.update({
        "root_cause": root_cause,
        "severity": determine_severity(root_cause, confidence),
        "root_cause_explanation": diagnosis.get(
            "root_cause_explanation",
            "Insufficient evidence to determine the root cause.",
        ),
        "confidence_explanation": diagnosis.get(
            "confidence_explanation",
            "Confidence is based on the relative strength of the evidence.",
        ),
        "data_completeness": diagnosis.get("data_completeness", 0.0),
        "evidence": evidence,
        "evidence_sources_detail": [
            {
                "agent_id": item.get("agent_id", "unknown"),
                "metric": item.get("metric", "unknown"),
            }
            for item in evidence
        ],
    })

    return required_report
