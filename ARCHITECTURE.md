# NetCoopAI Architecture

## Overview

NetCoopAI is a multi-agent network fault diagnosis prototype. It accepts network telemetry, analyzes it with specialist agents, correlates their findings, and produces an incident report. The application exposes a FastAPI backend and a Streamlit dashboard, with SQLite-backed diagnosis history.

## High-Level Workflow

```text
Telemetry Input
      |
      v
FastAPI Diagnosis API
      |
      v
Workflow Orchestrator
      |
      +----------------------+----------------------+----------------------+
      |                      |                      |
      v                      v                      v
Performance Agent     Infrastructure Agent    Connectivity Agent
      |                      |                      |
      +----------------------+----------------------+
                             |
                             v
                     Correlation Agent
                             |
                             v
                     Reporting Agent
                             |
                             v
                    Diagnosis Response
                             |
                +------------+------------+
                |                         |
                v                         v
         Streamlit Dashboard       SQLite History
```

## Components and Responsibilities

### FastAPI API layer

The API layer receives diagnosis requests, validates telemetry using Pydantic schemas, and returns diagnosis results. It also provides endpoints for viewing and exporting diagnosis history.

- `POST /api/diagnose` — run a diagnosis.
- `GET /api/history` — list stored diagnosis records.
- `GET /api/history/{record_id}` — retrieve a specific record.
- `GET /api/history/export.csv` — export history as CSV.

### Workflow orchestrator

`backend/orchestration/workflow.py` coordinates the diagnosis pipeline. It converts validated telemetry into a dictionary, calls the three specialist agents, passes their messages to the correlation agent, and sends the resulting diagnosis to the reporting agent. The final response includes the specialist agents' messages.

### Specialist agents

Each specialist analyzes the telemetry from a distinct perspective:

- **Performance agent** — evaluates performance-related telemetry.
- **Infrastructure agent** — evaluates infrastructure and device-health telemetry.
- **Connectivity agent** — evaluates connectivity-related telemetry.

The agents return structured messages for downstream correlation.

### Correlation agent

The correlation agent combines the specialist messages and telemetry into a unified diagnosis. It checks findings against the supplied telemetry, filters inconsistent findings, and scores possible causes using confidence and severity. Corroborating congestion findings receive an additional scoring bonus. The result includes a ranked diagnosis and alternatives when applicable.

### Reporting agent

The reporting agent formats the diagnosis into the incident report returned to the caller. The report includes the diagnosis and supporting information; the orchestrator also attaches the individual specialist-agent messages.

### Streamlit dashboard

The Streamlit frontend provides a user interface for submitting telemetry, viewing diagnosis results, and inspecting diagnosis history. It communicates with the FastAPI backend.

### Persistence

Diagnosis history is stored in SQLite using SQLAlchemy. The local database file is runtime data and should not be committed to the repository.

## Agent Communication Interfaces

The orchestrator passes telemetry as a dictionary to each specialist agent. Each specialist returns a structured message whose serialized form is included in the final report. The correlation agent consumes the list of specialist messages together with the original telemetry. The reporting agent consumes the validated telemetry and correlated diagnosis.

Pydantic schemas define and validate API input and output structures.

## Error Handling and Validation

- Incoming API data is validated before diagnosis.
- Invalid or missing required fields are rejected by the API with validation errors.
- Correlation checks findings against telemetry and filters inconsistent findings.
- The API and tests cover invalid inputs and diagnosis behavior.
- Diagnosis history is accessed through dedicated API endpoints.

## Running the Application

From the repository root, install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn backend.main:app --reload
```

In a second terminal, start the dashboard:

```powershell
streamlit run frontend/app.py
```

Run the sample scenarios from the repository root:

```powershell
python run_samples.py
```

Run the test suite:

```powershell
python -m pytest -q
```

## Sample Scenarios

The sample scenario file is `data/sample_scenarios.json`. The sample runner produces reports in `data/sample_reports/`, including normal, congestion, and outage examples.
