from backend.schemas import AgentMessage, AgentFinding


def analyze_infrastructure(telemetry: dict) -> AgentMessage:
    """Analyze device health metrics and return a standardized message."""

    metrics = telemetry.get("metrics", {})
    incident_id = telemetry.get("incident_id", "INC-UNKNOWN")

    findings = []
    probable_causes = []

    # CPU usage
    cpu = metrics.get("cpu_usage_pct")
    if isinstance(cpu, (int, float)) and cpu >= 90:
        findings.append(
            AgentFinding(
                metric="cpu_usage_pct",
                value=cpu,
                unit="%",
                severity="critical" if cpu >= 98 else "high",
                interpretation=f"High CPU usage detected: {cpu}%",
            )
        )
        probable_causes.append("device_cpu_overload")

    # Memory usage
    memory = metrics.get("memory_usage_pct")
    if isinstance(memory, (int, float)) and memory >= 90:
        findings.append(
            AgentFinding(
                metric="memory_usage_pct",
                value=memory,
                unit="%",
                severity="critical" if memory >= 98 else "high",
                interpretation=f"High memory usage detected: {memory}%",
            )
        )
        probable_causes.append("device_memory_pressure")

    # Queue drops
    queue_drops = metrics.get("queue_drops")
    if isinstance(queue_drops, (int, float)) and queue_drops >= 100:
        findings.append(
            AgentFinding(
                metric="queue_drops",
                value=queue_drops,
                severity="critical" if queue_drops >= 1000 else "high",
                interpretation=f"Elevated queue drops detected: {queue_drops}",
            )
        )
        probable_causes.append("interface_queue_congestion")

    # Interface errors
    interface_errors = metrics.get("interface_errors")
    if isinstance(interface_errors, (int, float)) and interface_errors >= 50:
        findings.append(
            AgentFinding(
                metric="interface_errors",
                value=interface_errors,
                severity="critical" if interface_errors >= 500 else "high",
                interpretation=f"Elevated interface errors detected: {interface_errors}",
            )
        )
        probable_causes.append("interface_errors")

    if not findings:
        findings.append(
            AgentFinding(
                metric="infrastructure",
                value="within_thresholds",
                severity="normal",
                interpretation=(
                    "No supplied infrastructure metric crossed "
                    "the configured thresholds."
                ),
            )
        )

    return AgentMessage(
        incident_id=incident_id,
        agent_id="infrastructure_agent",
        findings=findings,
        probable_causes=probable_causes,
        confidence=0.8 if probable_causes else 0.6,
        limitations=[
            "Infrastructure analysis is limited to the supplied device metrics."
        ],
    )