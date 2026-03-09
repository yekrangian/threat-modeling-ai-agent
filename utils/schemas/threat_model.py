"""Pydantic models for Agent 2 (Threat Model) and micro-agent outputs."""
from pydantic import BaseModel, Field
from typing import Optional


class ThreatModelMetadata(BaseModel):
    """Metadata for the threat model."""
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class TrustBoundaryThreat(BaseModel):
    """Trust boundary in threat model."""
    id: str
    name: str
    description: Optional[str] = None
    component_ids: list[str] = Field(default_factory=list)


class AuthenticationThreat(BaseModel):
    """Authentication in threat model (what gets logged, session indicators)."""
    mechanism: str
    what_is_logged: list[str] = Field(default_factory=list)
    session_indicators: list[str] = Field(default_factory=list)


class SensitiveAssetThreat(BaseModel):
    """Sensitive asset / crown jewel in threat model."""
    id: str
    name: str
    description: Optional[str] = None
    business_impact: Optional[str] = None


class ExternalIntegrationThreat(BaseModel):
    """External integration / third-party surface in threat model."""
    id: str
    name: str
    type: Optional[str] = None
    credential_exposure_notes: Optional[str] = None


class LogSourceThreat(BaseModel):
    """Log source / telemetry in threat model."""
    id: str
    name: str
    exists: bool = True
    retention_notes: Optional[str] = None
    gap_notes: Optional[str] = None


class ArchitectureComponentThreat(BaseModel):
    """Architecture component in threat model."""
    id: str
    name: str
    data_sources: list[str] = Field(default_factory=list)
    log_verbosity: Optional[str] = None


class DataFlowThreat(BaseModel):
    """Data flow with detection points."""
    source_id: str
    target_id: str
    detection_points: list[str] = Field(default_factory=list)


class AttackPathStage(BaseModel):
    """Single stage in an attack path (e.g. initial_access)."""
    stage: str = Field(..., description="e.g. initial_access, persistence, lateral_movement, exfiltration")
    mitre_technique_ids: list[str] = Field(default_factory=list, description="e.g. T1078")
    ttps: list[str] = Field(default_factory=list)
    detection_opportunities: list[str] = Field(default_factory=list)


class AttackPath(BaseModel):
    """Full attack path with MITRE ATT&CK mapping."""
    id: str
    name: Optional[str] = None
    stages: list[AttackPathStage] = Field(default_factory=list)
    description: Optional[str] = None


class ThreatScenario(BaseModel):
    """Threat scenario with attacker objectives."""
    id: str
    attacker_objective: str
    kill_chain_stages: list[str] = Field(default_factory=list)
    iocs: list[str] = Field(default_factory=list)
    forensic_artifacts: list[str] = Field(default_factory=list)


class DetectionCoverageItem(BaseModel):
    """ATT&CK technique and whether it is detectable."""
    mitre_technique_id: str
    technique_name: Optional[str] = None
    detectable: bool = True
    blind_spot_notes: Optional[str] = None


class ResponsePlaybook(BaseModel):
    """Response playbook entry."""
    id: str
    name: str
    containment_actions: list[str] = Field(default_factory=list)
    evidence_preservation: list[str] = Field(default_factory=list)
    escalation_triggers: list[str] = Field(default_factory=list)


class MonitoringRecommendation(BaseModel):
    """Recommendation for alerts, hunting, or dashboards."""
    id: str
    type: str = Field(..., description="e.g. alert, threat_hunting_query, dashboard")
    description: str
    priority: Optional[str] = None


class ThreatModel(BaseModel):
    """Full threat model; assembled from micro-agent outputs."""
    metadata: ThreatModelMetadata = Field(default_factory=ThreatModelMetadata)
    architecture_components: list[ArchitectureComponentThreat] = Field(default_factory=list)
    data_flows: list[DataFlowThreat] = Field(default_factory=list)
    trust_boundaries: list[TrustBoundaryThreat] = Field(default_factory=list)
    authentication: list[AuthenticationThreat] = Field(default_factory=list)
    sensitive_assets: list[SensitiveAssetThreat] = Field(default_factory=list)
    external_integrations: list[ExternalIntegrationThreat] = Field(default_factory=list)
    log_sources: list[LogSourceThreat] = Field(default_factory=list)
    attack_paths: list[AttackPath] = Field(default_factory=list)
    threat_scenarios: list[ThreatScenario] = Field(default_factory=list)
    detection_coverage: list[DetectionCoverageItem] = Field(default_factory=list)
    response_playbooks: list[ResponsePlaybook] = Field(default_factory=list)
    monitoring_recommendations: list[MonitoringRecommendation] = Field(default_factory=list)


# --- Micro-agent output schemas (each agent produces one of these) ---


class ArchitectureOutput(BaseModel):
    """Output of Architecture & Flows micro-agent."""
    architecture_components: list[ArchitectureComponentThreat] = Field(default_factory=list)
    data_flows: list[DataFlowThreat] = Field(default_factory=list)
    trust_boundaries: list[TrustBoundaryThreat] = Field(default_factory=list)
    log_sources: list[LogSourceThreat] = Field(default_factory=list)


class AuthAssetsOutput(BaseModel):
    """Output of Auth & Assets micro-agent."""
    authentication: list[AuthenticationThreat] = Field(default_factory=list)
    sensitive_assets: list[SensitiveAssetThreat] = Field(default_factory=list)
    external_integrations: list[ExternalIntegrationThreat] = Field(default_factory=list)


class AttackPathsOutput(BaseModel):
    """Output of Attack Paths & Scenarios micro-agent."""
    attack_paths: list[AttackPath] = Field(default_factory=list)
    threat_scenarios: list[ThreatScenario] = Field(default_factory=list)


class DetectionResponseOutput(BaseModel):
    """Output of Detection & Response micro-agent."""
    detection_coverage: list[DetectionCoverageItem] = Field(default_factory=list)
    response_playbooks: list[ResponsePlaybook] = Field(default_factory=list)
    monitoring_recommendations: list[MonitoringRecommendation] = Field(default_factory=list)
