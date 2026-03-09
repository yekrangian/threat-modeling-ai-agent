"""Micro-agent: Auth & Assets. Extracts authentication, sensitive assets, external integrations."""
from pathlib import Path

from utils.openai_client import chat_with_structured_output
from utils.schemas.code_analysis import CodebaseFacts
from utils.schemas.threat_model import AuthAssetsOutput


def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent / "utils" / "prompts" / "auth_assets_agent.txt"
    return path.read_text(encoding="utf-8").strip()


def run(codebase_facts: CodebaseFacts, org_context: str | None = None) -> AuthAssetsOutput:
    """Produce authentication, sensitive_assets, external_integrations for the threat model."""
    system_prompt = _load_prompt()
    user_prompt = f"Codebase facts (JSON):\n{codebase_facts.model_dump_json(indent=2)}"
    if org_context:
        user_prompt += f"\n\nOptional organizational context:\n{org_context}"

    return chat_with_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=AuthAssetsOutput,
    )
