"""Pydantic models for Agent 1 (Code Analyzer) output."""
from pydantic import BaseModel, Field
from typing import Optional


class ArchitectureComponent(BaseModel):
    """A component of the system architecture."""
    id: str = Field(..., description="Unique component ID")
    name: str
    type: str = Field(..., description="e.g. API, database, service, frontend")
    description: Optional[str] = None
    data_sources: list[str] = Field(default_factory=list)
    log_verbosity: Optional[str] = None


class DataFlow(BaseModel):
    """Data flow between components visible to defenders."""
    source_id: str
    target_id: str
    description: Optional[str] = None
    detection_points: list[str] = Field(default_factory=list)


class TrustBoundary(BaseModel):
    """Trust boundary in the system."""
    id: str
    name: str
    description: Optional[str] = None
    component_ids: list[str] = Field(default_factory=list)


class Authentication(BaseModel):
    """Authentication mechanisms and what gets logged."""
    mechanism: str
    what_is_logged: list[str] = Field(default_factory=list)
    session_indicators: list[str] = Field(default_factory=list)


class SensitiveAsset(BaseModel):
    """Crown jewel or high-impact asset."""
    id: str
    name: str
    description: Optional[str] = None
    business_impact: Optional[str] = None


class ExternalIntegration(BaseModel):
    """Third-party integration and credential exposure risk."""
    id: str
    name: str
    type: Optional[str] = None
    credential_exposure_notes: Optional[str] = None


class LogSource(BaseModel):
    """Telemetry source and gaps."""
    id: str
    name: str
    exists: bool = True
    retention_notes: Optional[str] = None
    gap_notes: Optional[str] = None


class CodebaseFacts(BaseModel):
    """Structured output from Code Analyzer agent."""
    architecture_components: list[ArchitectureComponent] = Field(default_factory=list)
    data_flows: list[DataFlow] = Field(default_factory=list)
    trust_boundaries: list[TrustBoundary] = Field(default_factory=list)
    authentication: list[Authentication] = Field(default_factory=list)
    sensitive_assets: list[SensitiveAsset] = Field(default_factory=list)
    external_integrations: list[ExternalIntegration] = Field(default_factory=list)
    log_sources: list[LogSource] = Field(default_factory=list)
    summary: Optional[str] = Field(None, description="Brief summary of the codebase for downstream agents")
