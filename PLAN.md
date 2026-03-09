# Threat Modeling AI Agents — Plan & Approaches

**Goal:** A series of focused AI agents that take a codebase (and optional org context) and produce actionable threat models. **Stack:** OpenAI API + Pydantic only. No frameworks (no LangChain, no MCP as dependency). Production-ready, beyond MVP.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THREAT MODELING PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Codebase] ──► Agent 1: Code Analyzer ──► Structured code/arch facts       │
│       │                    │                                                 │
│       │                    ▼                                                 │
│       │         Agent 2: Threat Model Generator ──► YAML threat model        │
│       │                    │                                                 │
│  [Org context] ────────────┘                                                 │
│       │                    │                                                 │
│       ▼                    ▼                                                 │
│  Agent 3: Prioritizer / Gap Analyzer ──► Prioritized recommendations         │
│       │                    │                                                 │
│       ▼                    ▼                                                 │
│  Agent 4: Report / Playbook Generator ──► Markdown + playbooks               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Four agents, each with a single responsibility:**

| Agent | Input | Output | Purpose |
|-------|--------|--------|---------|
| **1. Code Analyzer** | Repo path (files, structure) | Pydantic model: components, data flows, auth, integrations | Extract facts from code for threat modeling |
| **2. Threat Model Generator** | Code facts + optional org context | YAML threat model (metadata, attack_paths, detection_coverage, etc.) | Produce detection/SOC-oriented threat model |
| **3. Gap & Prioritizer** | Threat model + optional detection inventory | Prioritized gaps, MITRE mappings, recommendations | Identify blind spots and priorities |
| **4. Report Generator** | Threat model + gaps | Markdown report + response playbooks | Executive summary, threat register, playbooks |

---

## 2. Approaches (Choose One or Hybrid)

### Approach A: Sequential pipeline (recommended for “real quick” + production)

- **Flow:** Codebase → Agent 1 → Agent 2 → (optional) Agent 3 → Agent 4.
- **Pros:** Simple to run, debug, and hand off; each step has clear inputs/outputs (Pydantic); easy to add retries and logging per step.
- **Cons:** No branching or “interview” loop (can add later).
- **Best for:** Getting to production fast with clear ownership per agent.

### Approach B: Single “orchestrator” agent that calls specialists

- **Flow:** One coordinator agent that decides “analyze code” → call Agent 1, “generate threat model” → call Agent 2, etc., with a shared state (e.g. a context dict or Pydantic model).
- **Pros:** Can add conditional steps (e.g. “if no org context, skip prioritizer”) or simple interview (one back-and-forth).
- **Cons:** More prompt engineering; harder to debug; still no heavy framework.
- **Best for:** When you want one entry point and more flexibility later.

### Approach C: Two-phase (code → model, then model → report)

- **Flow:** Phase 1: Agent 1 + Agent 2 (code → threat model). Phase 2: Agent 3 + Agent 4 (threat model → gaps + report). User can run phase 1 only or both.
- **Pros:** Clear separation; can run phase 1 in CI on every repo; phase 2 when you have detection inventory or org context.
- **Cons:** Slightly more concepts to explain.
- **Best for:** “Codebase in, threat model out” plus optional “full report when we have more context.”

**Recommendation:** Start with **Approach A** (sequential pipeline) and implement **Approach C** conceptually (phase 1 = code → threat model, phase 2 = gaps + report). Add an optional “interview” step later (e.g. one clarifying question per run) without introducing a framework.

---

## 3. Data Models (Pydantic) — Production-Ready

All cross-agent data is Pydantic. This gives you validation, serialization, and a stable contract.

### 3.1 Code Analyzer output (Agent 1)

- **File:** `utils/schemas/code_analysis.py`
- **Models:** e.g. `ArchitectureComponent`, `DataFlow`, `TrustBoundary`, `Authentication`, `ExternalIntegration`, `SensitiveAsset`, `CodebaseFacts`.
- **Source:** Derived from the “Analyzing Your Internal Software” section (architecture_components, data_flows, trust_boundaries, authentication, sensitive_assets, external_integrations, log_sources).

### 3.2 Threat model (Agent 2)

- **File:** `utils/schemas/threat_model.py`
- **Models:** Match the YAML structure from context: `metadata`, `architecture_components`, `data_flows`, `trust_boundaries`, `authentication`, `sensitive_assets`, `external_integrations`, `log_sources`, `attack_paths`, `threat_scenarios`, `detection_coverage`, `response_playbooks`, `monitoring_recommendations`.
- **Attack path:** e.g. `initial_access → persistence → lateral_movement → exfiltration` with TTPs and detection opportunities; use explicit IDs and MITRE ATT&CK technique IDs where applicable.

### 3.3 Gap & priorities (Agent 3)

- **File:** `utils/schemas/gaps.py`
- **Models:** e.g. `DetectionGap`, `PrioritizedRecommendation`, `GapAnalysisResult` (list of gaps + list of recommendations with priority: immediate / short-term / long-term).

### 3.4 Report (Agent 4)

- **File:** `utils/schemas/report.py`
- **Models:** Optional; can be Markdown strings + structured `ThreatRegisterEntry`, `PlaybookStep`. Prefer one canonical markdown report model if you want to validate sections.

---

## 4. Agent Implementation (OpenAI + Pydantic, No Frameworks)

- **HTTP client:** `httpx` or `urllib.request` (sync or async with `asyncio`) to call `https://api.openai.com/v1/chat/completions`.
- **Structured output:** Use OpenAI [structured outputs](https://platform.openai.com/docs/guides/structured-outputs) (response_format with JSON schema from Pydantic) so every agent returns a single Pydantic model. This avoids regex/parsing and is production-friendly.
- **Prompts:** Stored in `utils/prompts/` (e.g. `code_analyzer.txt`, `threat_model_generator.txt`, `gap_analyzer.txt`, `report_generator.txt`). Load at runtime; no framework needed.
- **Retries:** Exponential backoff on 429/5xx; max 3 retries.
- **Logging:** Structured logging (JSON or key-value) with request_id, agent_name, step, latency, token_usage (from OpenAI response).
- **Config:** Environment variables or a single `config.py` (e.g. `OPENAI_API_KEY`, `OPENAI_MODEL`, `MAX_TOKENS`). No framework required.

---

## 5. Codebase Ingestion

- **Input:** Path to repo (or list of file paths + content). No framework: use `pathlib` and `open()` to read files; optionally `.gitignore`-aware (manual or use a small ignore list).
- **Chunking:** To stay within context limits, either:
  - **Option 1:** Summarize per directory or per file type (e.g. “backend”, “frontend”, “infra”) with a small “index” agent that returns a short summary + list of important paths, then run Agent 1 on that summary + selected files.
  - **Option 2:** Truncate by importance (e.g. configs, auth, API routes, DB access) and pass a capped character count per file.
- **Output:** A single “codebase context” string or a minimal structure (e.g. list of `{ path, content_preview }`) passed into Agent 1’s prompt.

---

## 6. API and CLI (Production-Ready)

- **Backend (FastAPI):** Under `endpoints/`, e.g.:
  - `POST /analyze` — runs Agent 1 (code analysis). Input: repo path or uploaded tarball.
  - `POST /threat-model` — runs Agent 1 + 2; optional body: org context text. Returns threat model YAML + JSON.
  - `POST /full-report` — runs 1 → 2 → 3 → 4; optional: org context, detection inventory. Returns threat model + gaps + markdown report.
- **CLI:** e.g. `python -m cli threat-model --repo ./my-app [--org-context path]` and `python -m cli full-report --repo ./my-app`. Uses the same agent functions in `utils/` or `agents/`.
- **Idempotency / rate limits:** Optional: cache by `hash(repo_path + config)` for Agent 1; rate limit per API key or per tenant.

---

## 7. Production Checklist (Beyond MVP)

- **Structured outputs:** All agents return Pydantic; validated and logged.
- **Errors:** Catch API errors, timeouts, validation errors; return clear HTTP status and message; never expose raw keys.
- **Secrets:** `OPENAI_API_KEY` from env only; no keys in code or in prompts.
- **Observability:** Log request_id, agent, step, latency, token usage; optional: export to your logging/monitoring.
- **Tests:** Unit tests for Pydantic schemas; integration test that mocks OpenAI and runs pipeline end-to-end (e.g. small fixture repo).
- **Docs:** One-page README: how to run CLI, how to call API, env vars, and the four agents’ roles.

---

## 8. Suggested File Layout

```
threat-modeling-ai-agent/
├── utils/
│   ├── openai_client.py      # Thin wrapper: post to OpenAI, retries, parse JSON into Pydantic
│   ├── prompts/              # .txt or .jinja2 prompts per agent
│   ├── schemas/
│   │   ├── code_analysis.py
│   │   ├── threat_model.py
│   │   ├── gaps.py
│   │   └── report.py
│   └── codebase_loader.py    # Walk repo, build context string or chunk list
├── agents/
│   ├── code_analyzer.py      # Agent 1
│   ├── threat_model_generator.py
│   ├── gap_prioritizer.py
│   └── report_generator.py
├── endpoints/
│   └── threat_model.py       # FastAPI routes
├── cli.py                    # or cli/ with __main__.py
├── config.py
├── PLAN.md                   # This file
└── context.txt
```

---

## 9. Quick Start (What to Build First)

1. **Pydantic schemas** for code analysis and threat model (minimal subset: components, attack_paths, detection_coverage).
2. **OpenAI client** in `utils/openai_client.py` with structured output and retries.
3. **Agent 1 + Agent 2** with prompts from context (code → facts → threat model YAML).
4. **Codebase loader** that given a path returns a bounded context string.
5. **One endpoint** `POST /threat-model` and one CLI command that run 1 → 2 and return the threat model.
6. **Agent 3 + 4** and `POST /full-report` plus gap analysis and markdown report.

This keeps you on **OpenAI + Pydantic**, **no frameworks**, **codebase in → threat model (and optionally full report) out**, and sets you up for production with clear structure and room to add “interview” or MCP later without rewriting.
