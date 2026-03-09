"""Threat model generator: orchestrates micro-agents and assembles the full ThreatModel."""
import logging

from utils.schemas.code_analysis import CodebaseFacts
from utils.schemas.threat_model import (
    ThreatModel,
    ThreatModelMetadata,
    ArchitectureOutput,
    AuthAssetsOutput,
    AttackPathsOutput,
    DetectionResponseOutput,
)

from .architecture_agent import run as run_architecture
from .auth_assets_agent import run as run_auth_assets
from .attack_paths_agent import run as run_attack_paths
from .detection_response_agent import run as run_detection_response

logger = logging.getLogger(__name__)


def generate_threat_model(
    codebase_facts: CodebaseFacts,
    org_context: str | None = None,
    model_name: str | None = None,
) -> ThreatModel:
    """
    Run all threat-model micro-agents and assemble a single ThreatModel.
    Order: Architecture, Auth/Assets, Attack Paths (then Detection/Response uses attack paths).
    """
    metadata = ThreatModelMetadata(
        name=model_name or codebase_facts.summary or "Threat Model",
        description=codebase_facts.summary,
    )

    logger.info("Micro-agent 1/4: Architecture & Flows")
    arch = run_architecture(codebase_facts, org_context=org_context)

    logger.info("Micro-agent 2/4: Auth & Assets")
    auth = run_auth_assets(codebase_facts, org_context=org_context)

    logger.info("Micro-agent 3/4: Attack Paths & Scenarios")
    paths = run_attack_paths(codebase_facts, org_context=org_context)

    logger.info("Micro-agent 4/4: Detection & Response")
    detection = run_detection_response(codebase_facts, paths, org_context=org_context)

    return ThreatModel(
        metadata=metadata,
        architecture_components=arch.architecture_components,
        data_flows=arch.data_flows,
        trust_boundaries=arch.trust_boundaries,
        log_sources=arch.log_sources,
        authentication=auth.authentication,
        sensitive_assets=auth.sensitive_assets,
        external_integrations=auth.external_integrations,
        attack_paths=paths.attack_paths,
        threat_scenarios=paths.threat_scenarios,
        detection_coverage=detection.detection_coverage,
        response_playbooks=detection.response_playbooks,
        monitoring_recommendations=detection.monitoring_recommendations,
    )
