# NetCoop AI — Multi-Agent Network Fault Diagnosis

NetCoop AI is a prototype that uses multiple specialized agents to analyze network telemetry, identify potential faults, correlate evidence, and generate an incident diagnosis.

## Features

- Multi-agent analysis of network performance, infrastructure, and connectivity
- Evidence correlation and ranked root-cause hypotheses
- Incident report generation
- FastAPI backend and Streamlit frontend
- SQLite-based diagnosis history
- Sample scenarios and automated tests

## Architecture

1. **Performance Agent** — analyzes performance-related telemetry.
2. **Infrastructure Agent** — examines infrastructure health.
3. **Connectivity Agent** — evaluates connectivity issues.
4. **Correlation Agent** — combines agent findings and ranks likely causes.
5. **Reporting Agent** — generates the final incident report.
6. **Orchestration Workflow** — coordinates the agents and the diagnosis process.

## Requirements

- Python 3.12
- pip

## Setup

Clone the repository and enter the project directory:

```bash
git clone <https://github.com/abhradwip123/NetCoopAI>
cd NetCoopAI
```

Create and activate a virtual environment:

**Windows PowerShell**
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the application

Start the backend:

```bash
uvicorn backend.main:app --reload
```

Start the frontend in a second terminal:

```bash
streamlit run frontend/app.py
```

The FastAPI documentation is available at `http://127.0.0.1:8000/docs` by default.

## Run sample scenarios

```bash
python run_samples.py
```

Sample scenarios are located in `data/sample_scenarios.json`. Generated reports are stored in `data/sample_reports/`.

## Run tests

```bash
python -m pytest -q
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/diagnose` | Run a diagnosis |
| GET | `/api/history` | Retrieve diagnosis history |
| GET | `/api/history/{record_id}` | Retrieve a diagnosis record |
| GET | `/api/history/export.csv` | Export diagnosis history as CSV |

## Project Structure

```text
NetCoopAI/
├── backend/
│   ├── agents/
│   ├── orchestration/
│   ├── routes/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── frontend/
│   └── app.py
├── data/
│   ├── sample_scenarios.json
│   └── sample_reports/
├── tests/
├── requirements.txt
├── run_samples.py
└── README.md
```

## Project Status

This project is a prototype for demonstrating multi-agent network fault diagnosis. 
