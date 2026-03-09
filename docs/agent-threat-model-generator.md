# Threat Model Generator (Orchestrator)

**Module:** `agents.threat_model_generator`  
**Role:** Orchestrates the four threat-model micro-agents and assembles the full **`ThreatModel`**.

## Purpose

Takes **`CodebaseFacts`** (from the Code Analyzer) and runs the four micro-agents in a fixed order, then merges their outputs into a single **`ThreatModel`** with metadata. This is the single entry point used by the CLI for “generate threat model.”

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_facts` | `CodebaseFacts` | Output from the Code Analyzer. |
| `org_context` | `str` or `None` | Optional organizational context; passed to all micro-agents. |
| `model_name` | `str` or `None` | Optional name for the threat model metadata (default: summary or "Threat Model"). |

## Output

**Type:** `utils.schemas.threat_model.ThreatModel`

Contains all fields assembled from the micro-agents:

- **metadata** — name, version?, description? (description from `codebase_facts.summary`).
- **architecture_components**, **data_flows**, **trust_boundaries**, **log_sources** — from Architecture agent.
- **authentication**, **sensitive_assets**, **external_integrations** — from Auth & Assets agent.
- **attack_paths**, **threat_scenarios** — from Attack Paths agent.
- **detection_coverage**, **response_playbooks**, **monitoring_recommendations** — from Detection & Response agent.

## Execution Order

1. **Architecture & Flows** — `run_architecture(codebase_facts, org_context)`
2. **Auth & Assets** — `run_auth_assets(codebase_facts, org_context)`
3. **Attack Paths & Scenarios** — `run_attack_paths(codebase_facts, org_context)`
4. **Detection & Response** — `run_detection_response(codebase_facts, attack_paths_output, org_context)`

The Detection & Response agent receives the output of the Attack Paths agent so that detection coverage and playbooks align with the same MITRE technique IDs.

## Usage

```python
from agents.code_analyzer import analyze_codebase
from agents.threat_model_generator import generate_threat_model

facts = analyze_codebase("./my-repo")
model = generate_threat_model(facts)
model = generate_threat_model(facts, org_context="Fintech, SOC2.", model_name="MyApp Threat Model")
```

## Logging

Logs at INFO level for each micro-agent step (e.g. "Micro-agent 1/4: Architecture & Flows").

## Dependencies

- `agents.architecture_agent.run`
- `agents.auth_assets_agent.run`
- `agents.attack_paths_agent.run`
- `agents.detection_response_agent.run`
- `utils.schemas.code_analysis.CodebaseFacts`
- `utils.schemas.threat_model.ThreatModel`, `ThreatModelMetadata`, and all micro-agent output types
