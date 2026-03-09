# Agent Documentation

This folder documents each AI agent in the threat modeling pipeline.

| Agent | Module | Purpose |
|-------|--------|---------|
| [Code Analyzer](agent-code-analyzer.md) | `agents.code_analyzer` | Extract structured facts from a codebase |
| [Architecture & Flows](agent-architecture.md) | `agents.architecture_agent` | Refine structure and visibility for the threat model |
| [Auth & Assets](agent-auth-assets.md) | `agents.auth_assets_agent` | Extract authentication, crown jewels, external integrations |
| [Attack Paths & Scenarios](agent-attack-paths.md) | `agents.attack_paths_agent` | Map attacker behavior and MITRE ATT&CK |
| [Detection & Response](agent-detection-response.md) | `agents.detection_response_agent` | Define detection coverage, playbooks, monitoring |
| [Threat Model Generator](agent-threat-model-generator.md) | `agents.threat_model_generator` | Orchestrate micro-agents and assemble the full model |

**Pipeline order:** Code Analyzer → Threat Model Generator (which runs Architecture → Auth/Assets → Attack Paths → Detection/Response).
