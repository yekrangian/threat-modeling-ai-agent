# Architecture & Flows Agent

**Module:** `agents.architecture_agent`  
**Role:** Micro-agent 1/4 — refines codebase facts into threat-model structure and visibility.

## Purpose

Takes **`CodebaseFacts`** (from the Code Analyzer) and produces a threat-model view of the system: architecture components, data flows with detection points, trust boundaries, and log sources. Focus is on what defenders can see and where visibility gaps exist.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_facts` | `CodebaseFacts` | Structured output from the Code Analyzer. |
| `org_context` | `str` or `None` | Optional organizational context (e.g. industry, compliance). |

## Output

**Type:** `utils.schemas.threat_model.ArchitectureOutput`

| Field | Type | Description |
|-------|------|-------------|
| `architecture_components` | `list[ArchitectureComponentThreat]` | id, name, data_sources, log_verbosity. |
| `data_flows` | `list[DataFlowThreat]` | source_id, target_id, detection_points. |
| `trust_boundaries` | `list[TrustBoundaryThreat]` | id, name, description, component_ids. |
| `log_sources` | `list[LogSourceThreat]` | id, name, exists, retention_notes, gap_notes. |

## Usage

```python
from agents.code_analyzer import analyze_codebase
from agents.architecture_agent import run as run_architecture

facts = analyze_codebase("./my-repo")
arch = run_architecture(facts)
# Or with org context:
arch = run_architecture(facts, org_context="Financial services, PCI-DSS.")
```

## Prompt

Loaded from `utils/prompts/architecture_agent.txt`. Asks the model to preserve component IDs from the input where applicable and to emphasize detection points and log gaps.

## Dependencies

- `utils.openai_client.chat_with_structured_output`
- `utils.schemas.code_analysis.CodebaseFacts`
- `utils.schemas.threat_model.ArchitectureOutput`
