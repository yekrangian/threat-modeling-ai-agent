# Detection & Response Agent

**Module:** `agents.detection_response_agent`  
**Role:** Micro-agent 4/4 — defines detection coverage, response playbooks, and monitoring recommendations.

## Purpose

Consumes **`CodebaseFacts`** and **`AttackPathsOutput`** (from the Attack Paths agent) to produce detection coverage (which MITRE ATT&CK techniques are detectable and where blind spots are), response playbooks, and monitoring recommendations (alerts, threat-hunting queries, dashboards). Detection coverage is aligned with the same MITRE IDs used in the attack paths.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_facts` | `CodebaseFacts` | Structured output from the Code Analyzer. |
| `attack_paths_output` | `AttackPathsOutput` | Output from the Attack Paths agent (used for MITRE ID alignment). |
| `org_context` | `str` or `None` | Optional organizational context. |

## Output

**Type:** `utils.schemas.threat_model.DetectionResponseOutput`

| Field | Type | Description |
|-------|------|-------------|
| `detection_coverage` | `list[DetectionCoverageItem]` | mitre_technique_id, technique_name?, detectable, blind_spot_notes?. |
| `response_playbooks` | `list[ResponsePlaybook]` | id, name, containment_actions, evidence_preservation, escalation_triggers. |
| `monitoring_recommendations` | `list[MonitoringRecommendation]` | id, type (alert \| threat_hunting_query \| dashboard), description, priority?. |

## Usage

```python
from agents.code_analyzer import analyze_codebase
from agents.attack_paths_agent import run as run_attack_paths
from agents.detection_response_agent import run as run_detection_response

facts = analyze_codebase("./my-repo")
paths = run_attack_paths(facts)
detection = run_detection_response(facts, paths)
detection = run_detection_response(facts, paths, org_context="SOC uses Splunk.")
```

## Prompt

Loaded from `utils/prompts/detection_response_agent.txt`. Instructs the model to use the provided attack paths and scenarios when building detection_coverage so MITRE IDs match.

## Dependencies

- `utils.openai_client.chat_with_structured_output`
- `utils.schemas.code_analysis.CodebaseFacts`
- `utils.schemas.threat_model.AttackPathsOutput`, `DetectionResponseOutput`
