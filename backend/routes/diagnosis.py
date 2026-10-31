
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DiagnosisHistory
from backend.schemas import DiagnosisRequest
from backend.orchestration.workflow import run_diagnosis
import csv
from io import StringIO

from fastapi.responses import Response

router = APIRouter()


@router.post("/diagnose")
def diagnose(
    request: DiagnosisRequest,
    db: Session = Depends(get_db),
):
    """Run diagnosis, save the report, and return it."""

    try:
        report = run_diagnosis(request.telemetry)

        record = DiagnosisHistory(
            incident_id=request.telemetry.incident_id,
            device_id=request.telemetry.device_id,
            root_cause=str(report.get("root_cause", "unknown")),
            severity=str(report.get("severity", "unknown")),
            confidence=float(report.get("confidence", 0.0)),
            report_json=json.dumps(report),
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return report

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis failed: {str(exc)}",
        ) from exc


@router.get("/history")
def get_diagnosis_history(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Return recent diagnosis history."""

    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 200",
        )

    records = (
        db.query(DiagnosisHistory)
        .order_by(DiagnosisHistory.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": record.id,
            "incident_id": record.incident_id,
            "device_id": record.device_id,
            "root_cause": record.root_cause,
            "severity": record.severity,
            "confidence": record.confidence,
            "created_at": (
                record.created_at.isoformat()
                if record.created_at
                else None
            ),
        }
        for record in records
    ]

@router.get("/history/export.csv")
def export_history_csv(db: Session = Depends(get_db)):
    records = (
        db.query(DiagnosisHistory)
        .order_by(DiagnosisHistory.created_at.desc())
        .all()
    )

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Incident ID",
        "Device ID",
        "Root Cause",
        "Severity",
        "Confidence",
        "Created At",
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.incident_id,
            record.device_id,
            record.root_cause,
            record.severity,
            record.confidence,
            record.created_at.isoformat() if record.created_at else "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="netcoop_diagnosis_history.csv"'
        },
    )

@router.get("/history/{record_id}")
def get_diagnosis_history_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """Return the full saved report for one history record."""

    record = (
        db.query(DiagnosisHistory)
        .filter(DiagnosisHistory.id == record_id)
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Diagnosis history record not found",
        )

    return json.loads(record.report_json)

