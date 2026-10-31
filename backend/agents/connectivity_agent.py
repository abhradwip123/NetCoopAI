from backend.schemas import AgentMessage, AgentFinding


def analyze_connectivity(telemetry: dict) -> AgentMessage:
    """Analyze device status and topology for connectivity problems."""

    incident_id = telemetry.get("incident_id", "INC-UNKNOWN")
    device_id = telemetry.get("device_id", "UNKNOWN-DEVICE")
    status = str(telemetry.get("status", "Unknown")).strip().lower()
    topology = telemetry.get("topology", {})

    findings = []
    probable_causes = []
    limitations = []

    # Check device status
    if status in {"down", "offline", "unreachable"}:
        findings.append(
            AgentFinding(
                metric="device_status",
                value=status,
                severity="critical",
                interpretation=f"Device {device_id} is reported as {status}.",
            )
        )
        probable_causes.append("device_unreachable")

    elif status in {"degraded", "warning"}:
        findings.append(
            AgentFinding(
                metric="device_status",
                value=status,
                severity="medium",
                interpretation=f"Device {device_id} is reported as {status}.",
            )
        )
        probable_causes.append("device_degraded")

    # Extract neighboring devices when topology is available
    neighbors = topology.get("neighbors", [])

    if isinstance(neighbors, list) and neighbors:
        findings.append(
            AgentFinding(
                metric="topology_neighbors",
                value=neighbors,
                severity="normal",
                interpretation=(
                    f"Topology lists {len(neighbors)} neighboring device(s) "
                    f"for {device_id}."
                ),
            )
        )
    else:
        limitations.append("No neighboring-device information was supplied.")

    if not findings:
        findings.append(
            AgentFinding(
                metric="connectivity",
                value="no_issue_detected",
                severity="normal",
                interpretation=(
                    "No connectivity issue was detected from the supplied "
                    "device status and topology."
                ),
            )
        )

    return AgentMessage(
        incident_id=incident_id,
        agent_id="connectivity_agent",
        findings=findings,
        probable_causes=probable_causes,
        confidence=0.85 if probable_causes else 0.6,
        limitations=limitations,
    )