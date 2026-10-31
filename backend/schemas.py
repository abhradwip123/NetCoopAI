from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MetricsInput(BaseModel):
    latency_ms: float | None = Field(default=None, ge=0)
    packet_loss_pct: float | None = Field(default=None, ge=0, le=100)
    jitter_ms: float | None = Field(default=None, ge=0)
    link_utilization_pct: float | None = Field(default=None, ge=0, le=100)
    cpu_usage_pct: float | None = Field(default=None, ge=0, le=100)
    memory_usage_pct: float | None = Field(default=None, ge=0, le=100)
    queue_drops: int | None = Field(default=None, ge=0)
    interface_errors: int | None = Field(default=None, ge=0)


class TelemetryInput(BaseModel):
    incident_id: str = Field(min_length=1, max_length=100)
    device_id: str = Field(min_length=1, max_length=100)
    status: Literal["up", "down", "degraded"]

    metrics: MetricsInput = Field(default_factory=MetricsInput)
    topology: dict = Field(default_factory=dict)

    @field_validator("incident_id", "device_id")
    @classmethod
    def identifiers_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

    @field_validator("topology")
    @classmethod
    def clean_topology(cls, topology: dict) -> dict:
        neighbors = topology.get("neighbors", [])

        if isinstance(neighbors, list):
            cleaned = [
                neighbor.strip()
                for neighbor in neighbors
                if isinstance(neighbor, str) and neighbor.strip()
            ]
            topology["neighbors"] = list(dict.fromkeys(cleaned))

        return topology


class AgentFinding(BaseModel):
    metric: str
    value: object
    severity: Literal[
        "normal", "low", "medium", "high", "critical"
    ]
    interpretation: str
    unit: str | None = None


class AgentMessage(BaseModel):
    incident_id: str
    agent_id: str
    findings: list[AgentFinding] = Field(default_factory=list)
    probable_causes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    limitations: list[str] = Field(default_factory=list)


class DiagnosisRequest(BaseModel):
    telemetry: TelemetryInput