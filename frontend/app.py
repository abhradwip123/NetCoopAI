
import json

import requests
import streamlit as st
import requests
import streamlit as st

# Use your existing API base URL variable if you already have one.
API_BASE_URL = "http://localhost:8000/api"

try:
    response = requests.get(
        f"{API_BASE_URL}/history/export.csv",
        timeout=30,
    )
    response.raise_for_status()

    st.download_button(
        label="Download History as CSV",
        data=response.content,
        file_name="netcoop_diagnosis_history.csv",
        mime="text/csv",
    )
except requests.RequestException as exc:
    st.error(f"Could not export diagnosis history: {exc}")

API_URL = "http://127.0.0.1:8000/api/diagnose"
HISTORY_API_URL = "http://127.0.0.1:8000/api/history"

SCENARIOS = {
    "Custom": {
        "status": "up",
        "metrics": {
            "latency_ms": 280,
            "packet_loss_pct": 5,
            "jitter_ms": 45,
            "link_utilization_pct": 94,
            "cpu_usage_pct": 96,
            "memory_usage_pct": 72,
            "queue_drops": 250,
            "interface_errors": 80,
        },
    },
    "Normal Network": {
        "status": "up",
        "metrics": {
            "latency_ms": 20,
            "packet_loss_pct": 0,
            "jitter_ms": 5,
            "link_utilization_pct": 40,
            "cpu_usage_pct": 30,
            "memory_usage_pct": 45,
            "queue_drops": 0,
            "interface_errors": 0,
        },
    },
    "Congestion": {
        "status": "up",
        "metrics": {
            "latency_ms": 280,
            "packet_loss_pct": 5,
            "jitter_ms": 45,
            "link_utilization_pct": 94,
            "cpu_usage_pct": 96,
            "memory_usage_pct": 72,
            "queue_drops": 250,
            "interface_errors": 80,
        },
    },
    "Device Outage": {
        "status": "down",
        "metrics": {
            "latency_ms": 0,
            "packet_loss_pct": 0,
            "jitter_ms": 0,
            "link_utilization_pct": 0,
            "cpu_usage_pct": 0,
            "memory_usage_pct": 0,
            "queue_drops": 0,
            "interface_errors": 0,
        },
    },
}


def render_severity_breakdown(agent_messages):
    """Display finding counts grouped by agent and severity."""
    st.subheader("Severity Breakdown by Agent")

    if not isinstance(agent_messages, list) or not agent_messages:
        st.info("No agent findings are available.")
        return

    severity_levels = ["critical", "high", "medium", "low", "normal"]

    for message in agent_messages:
        if not isinstance(message, dict):
            continue

        agent_id = message.get("agent_id", "Unknown Agent")
        findings = message.get("findings", [])

        if not isinstance(findings, list):
            findings = []

        counts = {severity: 0 for severity in severity_levels}

        for finding in findings:
            if not isinstance(finding, dict):
                continue

            severity = str(finding.get("severity", "unknown")).lower()
            if severity in counts:
                counts[severity] += 1

        with st.expander(agent_id.replace("_", " ").title()):
            cols = st.columns(len(severity_levels))

            for col, severity in zip(cols, severity_levels):
                with col:
                    st.metric(severity.title(), counts[severity])

            if findings:
                st.markdown("**Findings**")
                for finding in findings:
                    if not isinstance(finding, dict):
                        continue

                    metric = finding.get("metric", "Unknown metric")
                    value = finding.get("value", "N/A")
                    severity = str(
                        finding.get("severity", "unknown")
                    ).upper()
                    interpretation = finding.get(
                        "interpretation", "No interpretation provided."
                    )

                    st.write(
                        f"- **{metric}** ({severity}): "
                        f"{value} — {interpretation}"
                    )
            else:
                st.caption("This agent reported no findings.")
def load_diagnosis_history():
    """Fetch saved diagnosis summaries from the backend."""
    try:
        response = requests.get(
            HISTORY_API_URL,
            params={"limit": 100},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Support either a direct list or a wrapped response.
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("history", data.get("records", []))

        return []

    except requests.exceptions.RequestException as exc:
        st.warning(f"Could not load diagnosis history: {exc}")
        return []
def load_history_report(record_id):
    """Fetch the complete saved report for a history record."""
    try:
        response = requests.get(
            f"{HISTORY_API_URL}/{record_id}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        st.error(f"Could not load saved diagnosis: {exc}")
        return None

st.set_page_config(
    page_title="NetCoop AI",
    page_icon="🌐",
    layout="wide",
)

st.title("NetCoop AI")
st.caption("Multi-agent network fault diagnosis")

scenario_name = st.selectbox(
    "Load a demo scenario",
    list(SCENARIOS.keys()),
)

scenario = SCENARIOS[scenario_name]
default_metrics = scenario["metrics"]


with st.form("telemetry_form"):
    st.subheader("Incident Information")

    incident_id = st.text_input("Incident ID", value="INC-001")
    device_id = st.text_input("Device ID", value="RTR_CORE_1")

    status = st.selectbox(
        "Device Status",
        ["up", "degraded", "down", "unknown"],
        index=["up", "degraded", "down", "unknown"].index(
            scenario["status"]
        ),
    )

    st.subheader("Performance Metrics")

    col1, col2 = st.columns(2)

    with col1:
        latency = st.number_input(
            "Latency (ms)",
            min_value=0.0,
            value=float(default_metrics["latency_ms"]),
        )
        packet_loss = st.number_input(
            "Packet Loss (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_metrics["packet_loss_pct"]),
        )
        jitter = st.number_input(
            "Jitter (ms)",
            min_value=0.0,
            value=float(default_metrics["jitter_ms"]),
        )
        utilization = st.number_input(
            "Link Utilization (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_metrics["link_utilization_pct"]),
        )

    with col2:
        cpu = st.number_input(
            "CPU Usage (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_metrics["cpu_usage_pct"]),
        )
        memory = st.number_input(
            "Memory Usage (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(default_metrics["memory_usage_pct"]),
        )
        queue_drops = st.number_input(
            "Queue Drops",
            min_value=0,
            value=int(default_metrics["queue_drops"]),
        )
        interface_errors = st.number_input(
            "Interface Errors",
            min_value=0,
            value=int(default_metrics["interface_errors"]),
        )

    st.subheader("Topology")

    neighbors_text = st.text_input(
        "Neighbor Device IDs (comma-separated)",
        value="SW_CAMPUS_1, RTR_CORE_2",
    )

    submitted = st.form_submit_button("Diagnose Network")


if submitted:
    neighbors = [
        neighbor.strip()
        for neighbor in neighbors_text.split(",")
        if neighbor.strip()
    ]

    payload = {
        "telemetry": {
            "incident_id": incident_id,
            "device_id": device_id,
            "status": status,
            "metrics": {
                "latency_ms": latency,
                "packet_loss_pct": packet_loss,
                "jitter_ms": jitter,
                "link_utilization_pct": utilization,
                "cpu_usage_pct": cpu,
                "memory_usage_pct": memory,
                "queue_drops": queue_drops,
                "interface_errors": interface_errors,
            },
            "topology": {"neighbors": neighbors},
        }
    }

    with st.spinner("Agents are analyzing the telemetry..."):
        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                report = response.json()
                st.session_state["latest_diagnosis"] = {
                    "incident_id": incident_id,
                    "device_id": device_id,
                    "report": report,
                }

                st.success("Diagnosis completed")
                st.subheader("Diagnosis Summary")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Root Cause",
                        report.get("root_cause", "Unknown"),
                    )

                with col2:
                    st.metric(
                        "Severity",
                        report.get("severity", "Unknown"),
                    )

                with col3:
                    confidence = float(report.get("confidence", 0.0))
                    st.metric(
                        "Confidence Indicator",
                        f"{confidence:.0%}",
                    )

                confidence_explanation = report.get(
                    "confidence_explanation",
                    "No confidence explanation available.",
                )
                st.info(
                    f"**Why this confidence?** "
                    f"{confidence_explanation}"
                )

                data_completeness = report.get("data_completeness")

                if data_completeness is not None:
                    completeness = max(
                        0.0,
                        min(float(data_completeness), 1.0),
                    )

                    st.metric(
                        "Telemetry Completeness",
                        f"{completeness:.0%}",
                    )
                    st.progress(completeness)
                else:
                    st.caption(
                        "Telemetry completeness information is unavailable."
                    )

                st.write(
                    report.get("root_cause_explanation", "")
                )

                st.subheader("Affected Devices")
                st.write(
                    ", ".join(report.get("affected_devices", []))
                    or "No affected devices reported."
                )

                st.subheader("Recommended Actions")
                for action in report.get("recommended_actions", []):
                    st.write(f"- {action}")

                st.subheader("Alternative Causes")
                st.write(
                    ", ".join(report.get("alternative_causes", []))
                    or "No alternatives reported."
                )

                # New severity breakdown section
                render_severity_breakdown(
                    report.get("agent_messages", [])
                )

                with st.expander("Evidence"):
                    st.json(report.get("evidence", []))

                with st.expander("Agent Messages"):
                    st.json(report.get("agent_messages", []))

                with st.expander("Limitations"):
                    st.json(report.get("limitations", []))

                st.download_button(
                    "Download Diagnosis JSON",
                    data=json.dumps(report, indent=2),
                    file_name=f"{incident_id}_diagnosis.json",
                    mime="application/json",
                )

            else:
                st.error(
                    f"API returned HTTP {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.RequestException as exc:
            st.error(
                "Could not connect to the backend. "
                "Ensure FastAPI is running. "
                f"Details: {exc}"
            )
st.divider()
st.header("Diagnosis History")

history = load_diagnosis_history()

if not history:
    st.info("No saved diagnoses found yet.")
else:
    # Display a compact history table.
    history_rows = []

    for record in history:
        history_rows.append({
            "Record ID": record.get("id"),
            "Incident ID": record.get("incident_id", "Unknown"),
            "Device": record.get("device_id", "Unknown"),
            "Root Cause": record.get("root_cause", "Unknown"),
            "Severity": record.get("severity", "Unknown"),
            "Confidence": (
                f"{float(record.get('confidence', 0)):.0%}"
            ),
            "Created At": record.get("created_at", "Unknown"),
        })

    st.dataframe(
        history_rows,
        use_container_width=True,
        hide_index=True,
    )

    # Select a saved diagnosis to inspect.
    record_options = {
        (
            f"#{record.get('id')} | "
            f"{record.get('incident_id', 'Unknown')} | "
            f"{record.get('device_id', 'Unknown')} | "
            f"{record.get('root_cause', 'Unknown')}"
        ): record
        for record in history
    }

    selected_label = st.selectbox(
        "Select a previous diagnosis",
        list(record_options.keys()),
    )
    selected_record = record_options[selected_label]

    st.subheader("Selected Diagnosis")

    selected_report = load_history_report(selected_record["id"])

    if selected_report:
        with st.expander("View full saved report", expanded=True):
            st.json(selected_report)

    # Compare the selected history record with the latest diagnosis.
    latest = st.session_state.get("latest_diagnosis")

    if latest:
        st.subheader("Compare with Latest Diagnosis")

        latest_report = latest["report"]

        if selected_report:
            comparison = [
                {
                    "Field": "Incident ID",
                    "Selected": selected_report.get("incident_id", "Unknown"),
                    "Latest": latest_report.get("incident_id", "Unknown"),
                },
                {
                    "Field": "Device ID",
                    "Selected": selected_record.get("device_id", "Unknown"),
                    "Latest": latest.get("device_id", "Unknown"),
                },
                {
                    "Field": "Root Cause",
                    "Selected": selected_report.get("root_cause", "Unknown"),
                    "Latest": latest_report.get("root_cause", "Unknown"),
                },
                {
                    "Field": "Severity",
                    "Selected": selected_report.get("severity", "Unknown"),
                    "Latest": latest_report.get("severity", "Unknown"),
                },
                {
                    "Field": "Confidence",
                    "Selected": f"{float(selected_report.get('confidence', 0)):.0%}",
                    "Latest": f"{float(latest_report.get('confidence', 0)):.0%}",
                },
                {
                    "Field": "Evidence Count",
                    "Selected": len(selected_report.get("evidence", [])),
                    "Latest": len(latest_report.get("evidence", [])),
                },
                {
                    "Field": "Recommended Actions",
                    "Selected": len(selected_report.get("recommended_actions", [])),
                    "Latest": len(latest_report.get("recommended_actions", [])),
                },
            ]

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True,
            )

            with st.expander("Compare evidence"):
                st.write("**Selected diagnosis evidence**")
                st.json(selected_report.get("evidence", []))

                st.write("**Latest diagnosis evidence**")
                st.json(latest_report.get("evidence", []))

            with st.expander("Compare recommended actions"):
                st.write("**Selected diagnosis actions**")
                st.json(selected_report.get("recommended_actions", []))

                st.write("**Latest diagnosis actions**")
                st.json(latest_report.get("recommended_actions", []))