# Auth & Assets Agent

**Module:** `agents.auth_assets_agent`  
**Role:** Micro-agent 2/4 — extracts authentication, sensitive assets, and external integrations.

## Purpose

Consumes **`CodebaseFacts`** and produces the identity and asset-related parts of the threat model: how authentication works and what is logged, crown jewels (sensitive assets), and third-party integrations with credential exposure considerations.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `codebase_facts` | `CodebaseFacts` | Structured output from the Code Analyzer. |
| `org_context` | `str` or `None` | Optional organizational context. |

## Output

**Type:** `utils.schemas.threat_model.AuthAssetsOutput`

| Field | Type | Description |
|-------|------|-------------|
| `authentication` | `list[AuthenticationThreat]` | mechanism, what_is_logged, session_indicators. |
| `sensitive_assets` | `list[SensitiveAssetThreat]` | id, name, description, business_impact (crown jewels). |
| `external_integrations` | `list[ExternalIntegrationThreat]` | id, name, type, credential_exposure_notes. |

## Usage

```python
from agents.code_analyzer import analyze_codebase
from agents.auth_assets_agent import run as run_auth_assets

facts = analyze_codebase("./my-repo")
auth = run_auth_assets(facts)
auth = run_auth_assets(facts, org_context="Healthcare, HIPAA.")
```

## Prompt

Loaded from `utils/prompts/auth_assets_agent.txt`. Instructs the model to use explicit IDs (e.g. `asset-db-1`, `ext-payment-1`) and to call out credential exposure risks and session/auth logging.

## Dependencies

- `utils.openai_client.chat_with_structured_output`
- `utils.schemas.code_analysis.CodebaseFacts`
- `utils.schemas.threat_model.AuthAssetsOutput`
