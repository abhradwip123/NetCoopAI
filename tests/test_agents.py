from backend.schemas import TelemetryInput
from backend.orchestration.workflow import run_diagnosis
from backend.agents.reporting_agent import create_incident_report


def test_normal_network():
    telemetry = TelemetryInput(
        incident_id="TEST-NORMAL",
        device_id="RTR_1",
        status="up",
        metrics={
            "latency_ms": 20,
            "packet_loss_pct": 0,
            "jitter_ms": 5,
            "link_utilization_pct": 40,
            "cpu_usage_pct": 30,
            "memory_usage_pct": 45,
            "queue_drops": 0,
            "interface_errors": 0,
        },
        topology={"neighbors": ["SW_1"]},
    )

    report = run_diagnosis(telemetry)

    assert report["root_cause"] == "undetermined"
    assert report["confidence"] == 0.0


def test_congestion_scenario():
    telemetry = TelemetryInput(
        incident_id="TEST-CONGESTION",
        device_id="RTR_1",
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
        topology={"neighbors": ["SW_1"]},
    )

    report = run_diagnosis(telemetry)

    assert report["root_cause"] == "congestion"
    assert "link_utilization_pct" in [
        item["metric"] for item in report["evidence"]
    ]


def test_device_outage():
    telemetry = TelemetryInput(
        incident_id="TEST-OUTAGE",
        device_id="RTR_1",
        status="down",
        metrics={},
        topology={"neighbors": ["SW_1"]},
    )

    report = run_diagnosis(telemetry)

    assert report["root_cause"] == "device_unreachable"
    assert report["confidence"] > 0

def test_report_includes_device_and_neighbors():
    telemetry = TelemetryInput(
        incident_id="TEST-REPORT",
        device_id="RTR_1",
        status="up",
        metrics={},
        topology={"neighbors": ["SW_1", "SW_2", "SW_1"]},
    )

    report = create_incident_report(
        telemetry,
        {
            "root_cause": "congestion",
            "confidence": 0.8,
            "evidence": [],
            "ranked_causes": [],
        },
    )

    assert report["incident_id"] == "TEST-REPORT"
    assert report["affected_devices"] == ["RTR_1", "SW_1", "SW_2"]
    assert report["recommended_actions"]


def test_report_handles_missing_or_malformed_evidence():
    telemetry = TelemetryInput(
        incident_id="TEST-MISSING-EVIDENCE",
        device_id="RTR_1",
        status="up",
        metrics={},
        topology={},
    )

    report = create_incident_report(
        telemetry,
        {
            "root_cause": "undetermined",
            "evidence": "unexpected string",
            "ranked_causes": [None, {"cause": "congestion"}],
        },
    )

    assert report["evidence"] == []
    assert report["evidence_sources"] == []
    assert report["alternative_causes"] == ["congestion"]
    assert report["recommended_actions"]

def test_report_includes_confidence_explanation_and_completeness():
    telemetry = TelemetryInput(
        incident_id="TEST-CONFIDENCE",
        device_id="RTR_1",
        status="up",
        metrics={},
        topology={},
    )

    report = create_incident_report(
        telemetry,
        {
            "root_cause": "congestion",
            "confidence": 0.8,
            "confidence_explanation": "Strong evidence supports congestion.",
            "data_completeness": 0.75,
            "evidence": [],
            "ranked_causes": [],
        },
    )

    assert report["confidence_explanation"] == (
        "Strong evidence supports congestion."
    )
    assert report["data_completeness"] == 0.75

from backend.agents.correlation_agent import correlate_findings
from backend.schemas import AgentFinding, AgentMessage


def test_correlation_excludes_findings_that_mismatch_telemetry():
    message = AgentMessage(
        incident_id="INC-TEST",
        agent_id="performance_agent",
        findings=[
            AgentFinding(
                metric="latency_ms",
                value=999,
                unit="ms",
                severity="critical",
                interpretation="Elevated latency",
            )
        ],
        probable_causes=["latency_degradation"],
        confidence=0.9,
        limitations=[],
    )

    diagnosis = correlate_findings(
        [message],
        {
            "incident_id": "INC-TEST",
            "metrics": {"latency_ms": 20},
        },
    )

    assert diagnosis["root_cause"] == "undetermined"
    assert diagnosis["evidence"] == []
    assert any(
        "did not match the supplied telemetry" in limitation
        for limitation in diagnosis["limitations"]
    )

def test_diagnosis_handles_empty_metrics():
    telemetry = TelemetryInput(
        incident_id="TEST-EMPTY-METRICS",
        device_id="RTR_1",
        status="up",
        metrics={},
        topology={},
    )

    report = run_diagnosis(telemetry)

    assert report["root_cause"] == "undetermined"
    assert report["status"] == "insufficient_evidence"
    assert isinstance(report["evidence"], list)
    assert report["limitations"]


def test_diagnosis_handles_partial_metrics():
    telemetry = TelemetryInput(
        incident_id="TEST-PARTIAL-METRICS",
        device_id="RTR_1",
        status="up",
        metrics={"latency_ms": 25},
        topology={},
    )

    report = run_diagnosis(telemetry)

    assert report["root_cause"] == "undetermined"
    assert report["status"] == "insufficient_evidence"
    assert isinstance(report["evidence"], list)
    assert report["limitations"]
