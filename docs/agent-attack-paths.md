# Attack Paths & Scenarios Agent

**Module:** `agents.attack_paths_agent`  
**Role:** Micro-agent 3/4 — maps attacker behavior and MITRE ATT&CK to the system.

## Purpose

Takes **`CodebaseFacts`** and produces **attack paths** (with stages: initial_access → persistence → lateral_movement → exfiltration) and **threat scenarios**. Each stage is mapped to MITRE ATT&CK technique IDs and detection opportunities. Output is used by the Detection & Response agent to align coverage and playbooks.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_facts` | `CodebaseFacts` | Structured output from the Code Analyzer. |
| `org_context` | `str` or `None` | Optional organizational context. |

## Output

**Type:** `utils.schemas.threat_model.AttackPathsOutput`

| Field | Type | Description |
|-------|------|-------------|
| `attack_paths` | `list[AttackPath]` | id, name?, description?, stages (stage, mitre_technique_ids, ttps, detection_opportunities). |
| `threat_scenarios` | `list[ThreatScenario]` | id, attacker_objective, kill_chain_stages, iocs, forensic_artifacts. |

Attack path stages use names such as `initial_access`, `persistence`, `lateral_movement`, `exfiltration` and reference MITRE IDs (e.g. T1078).

## Usage

```python
from agents.code_analyzer import analyze_codebase
from agents.attack_paths_agent import run as run_attack_paths

facts = analyze_codebase("./my-repo")
paths = run_attack_paths(facts)
paths = run_attack_paths(facts, org_context="E-commerce, card data.")
```

## Prompt

Loaded from `utils/prompts/attack_paths_agent.txt`. Requires attack paths to be grounded in the given components and flows and to include detection opportunities per stage.

## Dependencies

- `utils.openai_client.chat_with_structured_output`
- `utils.schemas.code_analysis.CodebaseFacts`
- `utils.schemas.threat_model.AttackPathsOutput`
