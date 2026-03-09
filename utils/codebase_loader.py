"""Load codebase into a bounded context string for the Code Analyzer. No framework."""
import os
from pathlib import Path

# Default ignore patterns (simple substring match on path parts)
DEFAULT_IGNORE = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    ".pytest_cache",
    ".mypy_cache",
    "*.pyc",
    ".idea",
    ".vscode",
}


def _should_ignore(path: Path, ignore: set[str]) -> bool:
    parts = path.parts
    for part in parts:
        if part in ignore:
            return True
        if part.startswith(".") and part != ".gitignore":
            if part in ignore:
                return True
    return False


def load_codebase(
    repo_path: str | Path,
    max_file_size: int = 100_000,
    max_total_chars: int = 300_000,
    ignore: set[str] | None = None,
    extensions: set[str] | None = None,
) -> str:
    """
    Walk repo and build a single context string. Truncates per-file and total.
    Prioritizes: config, auth, API routes, DB, infra.
    """
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {repo_path}")

    ignore = ignore or DEFAULT_IGNORE
    # Include common code/config extensions if not specified
    if extensions is None:
        extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".yml", ".yaml",
            ".json", ".toml", ".env.example", ".md", ".sql", ".sh", ".dockerfile", ".tf",
        }

    total = 0
    parts: list[str] = []
    # Order: prefer certain paths so important files get in first
    priority_dirs = ("app", "src", "api", "routes", "auth", "config", "endpoints", "infra", "backend", "frontend")

    def sort_key(p: Path) -> tuple[int, str]:
        rel = p.relative_to(repo_path)
        s = str(rel).lower()
        for i, d in enumerate(priority_dirs):
            if d in s and (s.startswith(d) or f"/{d}/" in s or f"\\{d}\\" in s):
                return (i, s)
        return (len(priority_dirs), s)

    files: list[Path] = []
    for root, _, names in os.walk(repo_path, topdown=True):
        root_path = Path(root)
        if _should_ignore(root_path, ignore):
            continue
        for name in names:
            p = root_path / name
            if _should_ignore(p, ignore):
                continue
            suffix = p.suffix.lower()
            if suffix in extensions or (p.name.lower().endswith(".dockerfile") or "dockerfile" in p.name.lower()):
                try:
                    if p.stat().st_size <= max_file_size:
                        files.append(p)
                except OSError:
                    pass

    files.sort(key=sort_key)

    for p in files:
        if total >= max_total_chars:
            parts.append("\n\n... [truncated: max total characters reached]")
            break
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(text) > max_file_size:
            text = text[:max_file_size] + "\n\n... [truncated: file too long]"
        rel = p.relative_to(repo_path)
        block = f"\n\n--- FILE: {rel} ---\n{text}"
        if total + len(block) > max_total_chars:
            block = block[: max_total_chars - total - 80] + "\n\n... [truncated]"
        parts.append(block)
        total += len(block)

    if not parts:
        return f"[No readable files under {repo_path} with allowed extensions]"

    return f"# Codebase: {repo_path.name}\n" + "".join(parts).lstrip()
