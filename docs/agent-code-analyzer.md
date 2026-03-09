# Code Analyzer Agent

**Module:** `agents.code_analyzer`  
**Role:** Agent 1 — extracts structured facts from a codebase for threat modeling.

## Purpose

The Code Analyzer reads a repository (files under a given path), builds a bounded context string, and calls the OpenAI API to produce a single structured output: **`CodebaseFacts`**. It focuses on detection and response: what defenders can see, where trust boundaries are, what gets logged, and what an attacker might target.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `repo_path` | `str` or `Path` | Path to the repository (directory). |
| `max_file_size` | `int` or `None` | Max bytes per file to include (default from `config.MAX_FILE_SIZE_BYTES`, e.g. 100_000). |
| `max_total_chars` | `int` or `None` | Max total characters in the context sent to the model (default from `config.MAX_TOTAL_CHARS`, e.g. 300_000). |

The agent uses `utils.codebase_loader.load_codebase()` to walk the repo, filter by ignore list and extensions, and concatenate file contents into one string before sending it to the model.

## Output

**Type:** `utils.schemas.code_analysis.CodebaseFacts`

| Field | Type | Description |
|-------|------|-------------|
| `architecture_components` | `list[ArchitectureComponent]` | Components with id, name, type, data_sources, log_verbosity. |
| `data_flows` | `list[DataFlow]` | source_id, target_id, detection_points. |
| `trust_boundaries` | `list[TrustBoundary]` | id, name, component_ids. |
| `authentication` | `list[Authentication]` | mechanism, what_is_logged, session_indicators. |
| `sensitive_assets` | `list[SensitiveAsset]` | id, name, business_impact. |
| `external_integrations` | `list[ExternalIntegration]` | id, name, credential_exposure_notes. |
| `log_sources` | `list[LogSource]` | id, name, exists, retention_notes, gap_notes. |
| `summary` | `str` or `None` | Brief summary for downstream agents. |

## Usage

```python
from pathlib import Path
from agents.code_analyzer import analyze_codebase

facts = analyze_codebase(Path("./my-repo"))
# Optional: override limits
facts = analyze_codebase("./my-repo", max_file_size=50_000, max_total_chars=200_000)
```

## Prompt

Loaded from `utils/prompts/code_analyzer.txt`. Instructs the model to output a JSON object with the exact keys above and to use explicit IDs (e.g. `comp-api-1`, `comp-db-1`).

## Dependencies

- `utils.openai_client.chat_with_structured_output`
- `utils.codebase_loader.load_codebase`
- `utils.schemas.code_analysis.CodebaseFacts`
- `config.MAX_FILE_SIZE_BYTES`, `config.MAX_TOTAL_CHARS`
