from backend.schemas import TelemetryInput
from backend.agents.performance_agent import analyze_performance
from backend.agents.infrastructure_agent import analyze_infrastructure
from backend.agents.connectivity_agent import analyze_connectivity
from backend.agents.correlation_agent import correlate_findings
from backend.agents.reporting_agent import create_incident_report


def run_diagnosis(telemetry: TelemetryInput) -> dict:
    """Run the multi-agent network diagnosis workflow."""

    # Convert validated input into a dictionary for the agents.
    telemetry_data = telemetry.model_dump()

    # Step 1: Run specialist agents.
    agent_messages = [
        analyze_performance(telemetry_data),
        analyze_infrastructure(telemetry_data),
        analyze_connectivity(telemetry_data),
    ]

    # Step 2: Correlate their structured findings.
    diagnosis = correlate_findings(agent_messages, telemetry_data)

    # Step 3: Build the final incident report.
    report = create_incident_report(telemetry, diagnosis)

    # Include the individual agent messages for transparency.
    report["agent_messages"] = [
        message.model_dump() for message in agent_messages
    ]

    return report