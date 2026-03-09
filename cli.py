"""
CLI for threat modeling pipeline. Usage:
  python -m cli threat-model --repo ./my-app [--org-context path_or_text] [--output file] [--format yaml|json]
"""
import argparse
import json
import logging
import sys
from pathlib import Path

import yaml

# Ensure project root is on path when run as python -m cli
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.code_analyzer import analyze_codebase
from agents.threat_model_generator import generate_threat_model
from utils.schemas.threat_model import ThreatModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cli")


def run_threat_model_pipeline(
    repo_path: str | Path,
    org_context: str | None = None,
) -> ThreatModel:
    """Run Agent 1 (Code Analyzer) then Agent 2 (Threat Model Generator). Returns threat model."""
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repo_path}")

    logger.info("Step 1/2: Analyzing codebase at %s", repo_path)
    facts = analyze_codebase(repo_path)
    logger.info("Step 2/2: Generating threat model (4 micro-agents)")
    model = generate_threat_model(facts, org_context=org_context)
    return model


def _load_org_context(value: str) -> str | None:
    """If value is a path to a file, read it; otherwise return as-is."""
    p = Path(value)
    if p.is_file():
        return p.read_text(encoding="utf-8", errors="replace").strip()
    return value.strip() or None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Threat modeling from codebase: analyze repo and generate threat model (YAML/JSON).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command")

    # threat-model
    cmd = subparsers.add_parser("threat-model", help="Generate threat model from codebase (Agents 1 + 2)")
    cmd.add_argument(
        "--repo",
        required=True,
        metavar="PATH",
        help="Path to repository (directory)",
    )
    cmd.add_argument(
        "--org-context",
        metavar="TEXT_OR_FILE",
        help="Optional org context: literal text or path to a file",
    )
    cmd.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write output to this file (default: stdout)",
    )
    cmd.add_argument(
        "--format",
        "-f",
        choices=("yaml", "json"),
        default="yaml",
        help="Output format (default: yaml)",
    )

    args = parser.parse_args()

    if args.command == "threat-model":
        try:
            org_context = _load_org_context(args.org_context) if getattr(args, "org_context", None) else None
            model = run_threat_model_pipeline(args.repo, org_context=org_context)
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                logger.error("Set OPENAI_API_KEY environment variable.")
                return 1
            raise
        except NotADirectoryError as e:
            logger.error("%s", e)
            return 1

        data = model.model_dump(mode="json")

        if args.format == "yaml":
            out = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        else:
            out = json.dumps(data, indent=2, ensure_ascii=False)

        if getattr(args, "output", None):
            Path(args.output).write_text(out, encoding="utf-8")
            logger.info("Wrote %s", args.output)
        else:
            print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
