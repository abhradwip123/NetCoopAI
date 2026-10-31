
import json
from pathlib import Path

from backend.schemas import TelemetryInput
from backend.orchestration.workflow import run_diagnosis



def main():
    sample_file = Path("data/sample_scenarios.json")

    with sample_file.open("r", encoding="utf-8") as file:
        scenarios = json.load(file)

    output_dir = Path("data/sample_reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    for scenario in scenarios:
        telemetry = TelemetryInput(**scenario)

        report = run_diagnosis(telemetry)

        output_file = output_dir / f"{telemetry.incident_id}.json"
        output_file.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )

        print(f"\nScenario: {telemetry.incident_id}")
        print(f"Root cause: {report['root_cause']}")
        print(f"Status: {report['status']}")
        print(f"Saved report: {output_file}")


if __name__ == "__main__":
    main()
