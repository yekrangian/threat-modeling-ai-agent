# Threat Modeling AI Agents

Generate detection/SOC-oriented threat models from a codebase using OpenAI and Pydantic. No frameworks.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Set your API key:

```bash
set OPENAI_API_KEY=sk-...
```

Optional: `OPENAI_MODEL` (default: gpt-4o), `OPENAI_MAX_TOKENS`, `MAX_FILE_SIZE_BYTES`, `MAX_TOTAL_CHARS`.

## CLI (run from project root)

Generate a threat model from a repository:

```bash
python -m cli threat-model --repo C:\path\to\your\repo
```

Options:

- `--repo PATH` — Path to the repo (required).
- `--org-context TEXT_OR_FILE` — Optional: literal text or path to a file with org context.
- `--output FILE` / `-o` — Write output to file (default: stdout).
- `--format yaml|json` / `-f` — Output format (default: yaml).

Examples:

```bash
python -m cli threat-model --repo ./my-app -o threat-model.yaml
python -m cli threat-model --repo ./my-app --org-context ./org-context.txt -f json -o model.json
```

## Pipeline

1. **Agent 1 (Code Analyzer)** — Reads the repo, extracts architecture components, data flows, trust boundaries, auth, sensitive assets, external integrations, log sources → `CodebaseFacts`.
2. **Threat Model Generator (orchestrator)** — Runs four **micro-agents** and assembles the full threat model:
   - **Architecture & Flows** — `architecture_components`, `data_flows`, `trust_boundaries`, `log_sources`
   - **Auth & Assets** — `authentication`, `sensitive_assets`, `external_integrations`
   - **Attack Paths & Scenarios** — `attack_paths` (MITRE ATT&CK), `threat_scenarios`
   - **Detection & Response** — `detection_coverage`, `response_playbooks`, `monitoring_recommendations` (aligned with attack paths)

Each micro-agent has its own prompt and Pydantic output schema; the orchestrator merges their outputs into one `ThreatModel`. Output is a single YAML or JSON document suitable for SOC/detection engineering.

**Structured output:** The app uses OpenAI’s `chat.completions.parse()` endpoint with your Pydantic models as `response_format`, so responses are guaranteed to match the schema. Use a model that supports structured outputs (e.g. `gpt-4o` or `gpt-4o-2024-08-06` and later); set `OPENAI_MODEL` if needed.

## Documentation

Agent-level documentation lives in **[docs/](docs/)**:

- [docs/README.md](docs/README.md) — Index of all agents
- [Code Analyzer](docs/agent-code-analyzer.md)
- [Architecture & Flows](docs/agent-architecture.md)
- [Auth & Assets](docs/agent-auth-assets.md)
- [Attack Paths & Scenarios](docs/agent-attack-paths.md)
- [Detection & Response](docs/agent-detection-response.md)
- [Threat Model Generator (orchestrator)](docs/agent-threat-model-generator.md)
