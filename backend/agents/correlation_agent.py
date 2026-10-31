
from collections import defaultdict

from backend.schemas import AgentFinding, AgentMessage


CAUSE_EVIDENCE = {
    "device_unreachable": ["device_status"],
    "device_degraded": ["device_status"],
    "congestion": [
        "link_utilization_pct",
        "queue_drops",
        "packet_loss_pct",
        "latency_ms",
        "jitter_ms",
    ],
    "interface_queue_congestion": ["queue_drops"],
    "packet_loss": ["packet_loss_pct"],
    "latency_degradation": ["latency_ms"],
    "jitter": ["jitter_ms"],
    "device_cpu_overload": ["cpu_usage_pct"],
    "device_memory_pressure": ["memory_usage_pct"],
    "interface_errors": ["interface_errors"],
}

CAUSE_EXPLANATIONS = {
    "device_unreachable": "The device is reported as down or unreachable.",
    "device_degraded": "The device is reported as degraded.",
    "congestion": (
        "High link utilization and queue drops, potentially accompanied "
        "by packet loss or delay, suggest network congestion."
    ),
    "interface_queue_congestion": "Interface queue drops suggest congestion.",
    "packet_loss": "Packet loss is above the configured threshold.",
    "latency_degradation": "Latency is above the configured threshold.",
    "jitter": "Jitter is above the configured threshold.",
    "device_cpu_overload": "High CPU usage may impair device processing.",
    "device_memory_pressure": "High memory usage may impair device operation.",
    "interface_errors": "Interface errors may indicate a link or port problem.",
}

SEVERITY_WEIGHTS = {
    "medium": 1.0,
    "high": 2.0,
    "critical": 3.0,
}

EXPECTED_METRICS = {
    "latency_ms",
    "packet_loss_pct",
    "jitter_ms",
    "link_utilization_pct",
    "cpu_usage_pct",
    "memory_usage_pct",
    "queue_drops",
    "interface_errors",
}


def _finding_matches_telemetry(
    finding: AgentFinding,
    telemetry_data: dict,
) -> bool:
    """Check whether a finding matches the supplied telemetry."""

    if finding.metric in EXPECTED_METRICS:
        metrics = telemetry_data.get("metrics") or {}
        actual_value = metrics.get(finding.metric)

        if actual_value is None:
            return False

        return finding.value == actual_value

    if finding.metric == "device_status":
        actual_status = str(
            telemetry_data.get("status", "")
        ).strip().lower()

        return str(finding.value).strip().lower() == actual_status

    return True


def correlate_findings(
    messages: list[AgentMessage],
    telemetry_data: dict | None = None,
) -> dict:
    """Rank probable causes using direct evidence and symptom relationships."""

    telemetry_data = telemetry_data or {}

    cause_scores = defaultdict(float)
    cause_evidence = defaultdict(list)
    all_findings = []
    limitations = []

    incident_id = messages[0].incident_id if messages else "INC-UNKNOWN"

    # Collect only findings that match the supplied telemetry.
    for message in messages:
        for finding in message.findings:
            if not _finding_matches_telemetry(finding, telemetry_data):
                limitations.append(
                    f"Finding from {message.agent_id} for "
                    f"{finding.metric} did not match the supplied telemetry "
                    "and was excluded."
                )
                continue

            all_findings.append({
                "agent_id": message.agent_id,
                "metric": finding.metric,
                "value": finding.value,
                "unit": finding.unit,
                "severity": finding.severity,
                "interpretation": finding.interpretation,
            })

        # Score each cause using its matching supporting findings.
        for cause in message.probable_causes:
            expected_metrics = CAUSE_EVIDENCE.get(cause, [])

            matching_findings = [
                finding
                for finding in message.findings
                if finding.metric in expected_metrics
                and finding.severity in SEVERITY_WEIGHTS
                and _finding_matches_telemetry(finding, telemetry_data)
            ]

            if not matching_findings:
                continue

            strongest_weight = max(
                SEVERITY_WEIGHTS[finding.severity]
                for finding in matching_findings
            )

            cause_scores[cause] += message.confidence * strongest_weight

            cause_evidence[cause].extend(
                finding.metric for finding in matching_findings
            )

    # Cross-metric corroboration: high utilization + queue drops
    # supports congestion, but does not prove causation.
    metrics_by_name = {
        finding["metric"]: finding
        for finding in all_findings
    }

    utilization = metrics_by_name.get("link_utilization_pct")
    queue_drops = metrics_by_name.get("queue_drops")

    if (
        utilization
        and queue_drops
        and utilization["severity"] in {"high", "critical"}
        and queue_drops["severity"] in {"high", "critical"}
    ):
        cause_scores["congestion"] += 1.5
        cause_evidence["congestion"].extend(
            ["link_utilization_pct", "queue_drops"]
        )

        for metric in ("packet_loss_pct", "latency_ms", "jitter_ms"):
            finding = metrics_by_name.get(metric)
            if finding and finding["severity"] in {"high", "critical"}:
                cause_evidence["congestion"].append(metric)

    ranked_causes = sorted(
        cause_scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    if ranked_causes:
        top_cause, top_score = ranked_causes[0]
        second_score = (
            ranked_causes[1][1]
            if len(ranked_causes) > 1
            else 0.0
        )

        if top_score > 0:
            separation = (top_score - second_score) / top_score
            confidence = min(0.95, 0.5 + 0.45 * separation)
        else:
            separation = 0.0
            confidence = 0.0

        if len(ranked_causes) == 1:
            confidence_explanation = (
                "Only one cause was supported by the current findings. "
                "Additional telemetry could reveal other possible causes."
            )
        elif separation >= 0.5:
            confidence_explanation = (
                "The leading cause has substantially stronger evidence "
                "than the next-ranked cause."
            )
        else:
            confidence_explanation = (
                "Several causes have similar evidence scores, so the "
                "leading cause is not clearly separated from alternatives."
            )
    else:
        top_cause = "undetermined"
        confidence = 0.0
        confidence_explanation = (
            "No cause received sufficient supporting evidence."
        )

    metrics = telemetry_data.get("metrics") or {}

    observed_metrics = {
        metric
        for metric in EXPECTED_METRICS
        if metrics.get(metric) is not None
    }

    data_completeness = (
        len(observed_metrics) / len(EXPECTED_METRICS)
        if EXPECTED_METRICS
        else 0.0
    )

    return {
        "incident_id": incident_id,
        "root_cause": top_cause,
        "root_cause_explanation": CAUSE_EXPLANATIONS.get(
            top_cause,
            "Insufficient evidence to explain the likely cause.",
        ),
        "confidence": round(confidence, 2),
        "confidence_explanation": confidence_explanation,
        "data_completeness": round(data_completeness, 2),
        "ranked_causes": [
            {
                "cause": cause,
                "score": round(score, 2),
                "evidence_metrics": sorted(set(cause_evidence[cause])),
            }
            for cause, score in ranked_causes
        ],
        "evidence": all_findings,
        "limitations": sorted(set(limitations)),
    }
