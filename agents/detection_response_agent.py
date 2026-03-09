"""Micro-agent: Detection & Response. Defines detection coverage, playbooks, monitoring recommendations."""
from pathlib import Path

from utils.openai_client import chat_with_structured_output
from utils.schemas.code_analysis import CodebaseFacts
from utils.schemas.threat_model import AttackPathsOutput, DetectionResponseOutput


def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent / "utils" / "prompts" / "detection_response_agent.txt"
    return path.read_text(encoding="utf-8").strip()


def run(
    codebase_facts: CodebaseFacts,
    attack_paths_output: AttackPathsOutput,
    org_context: str | None = None,
) -> DetectionResponseOutput:
    """Produce detection_coverage, response_playbooks, monitoring_recommendations aligned with attack paths."""
    system_prompt = _load_prompt()
    user_prompt = (
        f"Codebase facts (JSON):\n{codebase_facts.model_dump_json(indent=2)}\n\n"
        f"Attack paths and scenarios (use these MITRE IDs for detection_coverage):\n"
        f"{attack_paths_output.model_dump_json(indent=2)}"
    )
    if org_context:
        user_prompt += f"\n\nOptional organizational context:\n{org_context}"

    return chat_with_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=DetectionResponseOutput,
    )
