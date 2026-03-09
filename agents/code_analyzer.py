"""Agent 1: Code Analyzer. Extracts structured facts from a codebase for threat modeling."""
from pathlib import Path

from utils.openai_client import chat_with_structured_output
from utils.schemas.code_analysis import CodebaseFacts
from utils.codebase_loader import load_codebase
from config import MAX_FILE_SIZE_BYTES, MAX_TOTAL_CHARS


def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent / "utils" / "prompts" / "code_analyzer.txt"
    return path.read_text(encoding="utf-8").strip()


def analyze_codebase(
    repo_path: str | Path,
    max_file_size: int | None = None,
    max_total_chars: int | None = None,
) -> CodebaseFacts:
    """
    Load codebase context and run Code Analyzer agent. Returns structured CodebaseFacts.
    """
    max_file_size = max_file_size or MAX_FILE_SIZE_BYTES
    max_total_chars = max_total_chars or MAX_TOTAL_CHARS

    context = load_codebase(repo_path, max_file_size=max_file_size, max_total_chars=max_total_chars)
    system_prompt = _load_prompt()
    user_prompt = f"Analyze the following codebase and output the JSON object only.\n\n{context}"

    return chat_with_structured_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=CodebaseFacts,
    )
