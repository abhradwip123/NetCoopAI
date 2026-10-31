
from backend.schemas import AgentMessage, AgentFinding


def analyze_performance(telemetry: dict) -> AgentMessage:
    """
    Analyze network performance metrics and return
    a standardized diagnostic message.
    """

    metrics = telemetry.get("metrics", {})
    incident_id = telemetry.get("incident_id", "INC-UNKNOWN")

    findings = []
    probable_causes = []

    # 1. Analyze latency
    latency = metrics.get("latency_ms")

    if latency is not None and latency >= 150:
        severity = "critical" if latency >= 500 else "high"

        findings.append(
            AgentFinding(
                metric="latency_ms",
                value=latency,
                unit="ms",
                severity=severity,
                interpretation=f"Elevated latency detected: {latency} ms",
            )
        )

        probable_causes.append("latency_degradation")

    # 2. Analyze packet loss
    packet_loss = metrics.get("packet_loss_pct")

    if packet_loss is not None and packet_loss >= 2:
        severity = "critical" if packet_loss >= 15 else "high"

        findings.append(
            AgentFinding(
                metric="packet_loss_pct",
                value=packet_loss,
                unit="%",
                severity=severity,
                interpretation=f"Elevated packet loss detected: {packet_loss}%",
            )
        )

        probable_causes.append("packet_loss")

    # 3. Analyze jitter
    jitter = metrics.get("jitter_ms")

    if jitter is not None and jitter >= 30:
        findings.append(
            AgentFinding(
                metric="jitter_ms",
                value=jitter,
                unit="ms",
                severity="high",
                interpretation=f"Elevated jitter detected: {jitter} ms",
            )
        )

        probable_causes.append("jitter")

    # 4. Analyze link utilization
    utilization = metrics.get("link_utilization_pct")

    if utilization is not None and utilization >= 85:
        severity = "critical" if utilization >= 95 else "high"

        findings.append(
            AgentFinding(
                metric="link_utilization_pct",
                value=utilization,
                unit="%",
                severity=severity,
                interpretation=f"High link utilization detected: {utilization}%",
            )
        )

        probable_causes.append("congestion")

    # 5. Report normal performance if no thresholds were crossed
    if not findings:
        findings.append(
            AgentFinding(
                metric="performance",
                value="within_thresholds",
                severity="normal",
                interpretation=(
                    "No supplied performance metric crossed "
                    "the configured thresholds."
                ),
            )
        )

    return AgentMessage(
        incident_id=incident_id,
        agent_id="performance_agent",
        findings=findings,
        probable_causes=list(set(probable_causes)),
        confidence=0.8 if probable_causes else 0.6,
        limitations=[
            "Diagnosis is based only on the supplied telemetry."
        ],
    )
