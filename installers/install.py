#!/usr/bin/env python3
"""Cross-agent installer for study-design-skills.

Supports: Claude Code, Codex, OpenCode, OpenClaw, Hermes.

Usage:
  python installers/install.py                     # install for all detected agents
  python installers/install.py --target claude      # specific agent only
  python installers/install.py --self-test          # dry-run validation
  python installers/install.py --verbose            # detailed output
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "study-design-skills"
SKILL_SRC = REPO_ROOT / "skills" / SKILL_NAME

# Agent skill target directories
AGENT_PATHS: dict[str, Path] = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "opencode": Path.home() / ".opencode" / "skills",
    "openclaw": Path.home() / ".openclaw" / "skills",
    "hermes": Path.home() / ".hermes" / "skills",
}

MANIFEST_LABELS: dict[str, str] = {
    "claude": ".claude-plugin/marketplace.json",
    "codex": ".plugin.json",
    "opencode": "plugin.yaml",
    "openclaw": ".plugin.json",
    "hermes": ".plugin.json",
}


def detect_installed_agents() -> list[str]:
    """Return agents whose config directories already exist."""
    return [name for name, path in AGENT_PATHS.items() if path.exists()]


def install_skill(target: str, verbose: bool = False) -> bool:
    """Copy the skill directory into the target agent's skills directory."""
    dest_dir = AGENT_PATHS[target] / SKILL_NAME
    if not SKILL_SRC.is_dir():
        print(f"  ERROR: source skill directory not found: {SKILL_SRC}", file=sys.stderr)
        return False

    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(SKILL_SRC, dest_dir, symlinks=True, dirs_exist_ok=True)
    ok = (dest_dir / "SKILL.md").is_file()
    status = "OK" if ok else "FAILED (SKILL.md missing after copy)"
    if verbose or not ok:
        print(f"  {'✔' if ok else '✘'} {target:<10} -> {dest_dir}  {status}")
    return ok


def register_plugin(target: str, verbose: bool = False) -> bool:
    """Register the plugin manifest in the agent's plugin registry."""
    dest_dir = AGENT_PATHS[target] / SKILL_NAME
    manifest_key = MANIFEST_LABELS.get(target)

    if not manifest_key:
        if verbose:
            print(f"  ~ {target:<10} no manifest registration defined")
        return True

    if target == "claude":
        # Claude Code: register in ~/.claude/plugins.json
        plugins_file = Path.home() / ".claude" / "plugins.json"
        entry = {
            "name": SKILL_NAME,
            "source": str(dest_dir),
            "skills": [str(dest_dir)],
        }
        if plugins_file.exists():
            registry = json.loads(plugins_file.read_text(encoding="utf-8"))
        else:
            registry = {"plugins": []}
        # Remove old entry if exists, then append
        registry["plugins"] = [p for p in registry["plugins"] if p.get("name") != SKILL_NAME]
        registry["plugins"].append(entry)
        plugins_file.parent.mkdir(parents=True, exist_ok=True)
        plugins_file.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        if verbose:
            print(f"  ✔ {target:<10} registered in {plugins_file}")
    elif target == "opencode":
        # OpenCode: copy plugin.yaml into skill dir
        src = REPO_ROOT / "plugin.yaml"
        if src.is_file():
            shutil.copy2(src, dest_dir / "plugin.yaml")
            if verbose:
                print(f"  ✔ {target:<10} plugin.yaml copied")
    else:
        # Codex, OpenClaw, Hermes: copy .plugin.json into skill dir
        src = REPO_ROOT / ".plugin.json"
        if src.is_file():
            shutil.copy2(src, dest_dir / ".plugin.json")
            if verbose:
                print(f"  ✔ {target:<10} .plugin.json copied")
    return True


def install(target: str, verbose: bool = False) -> int:
    """Install for one target. Returns 0 on success, 1 on failure."""
    if not install_skill(target, verbose):
        return 1
    register_plugin(target, verbose)
    return 0


def self_test(verbose: bool = False) -> int:
    """Validate skill directory integrity without installing."""
    errors: list[str] = []

    required_dirs = [
        SKILL_SRC,
        SKILL_SRC / "references",
        SKILL_SRC / "scripts",
        SKILL_SRC / "schemas",
        SKILL_SRC / "evals",
        SKILL_SRC / "evals" / "rubrics",
    ]
    required_files = [
        SKILL_SRC / "SKILL.md",
        SKILL_SRC / "schemas" / "study-package.schema.json",
    ]
    recommended = [
        SKILL_SRC / "references" / "route-registry.json",
        SKILL_SRC / "references" / "reporting-checklists-index.md",
        SKILL_SRC / "references" / "checklists",
    ]

    for d in required_dirs:
        if not d.is_dir():
            errors.append(f"MISSING_DIR: {d}")
    for f in required_files:
        if not f.is_file():
            errors.append(f"MISSING_FILE: {f}")
    for r in recommended:
        if not r.exists() and verbose:
            print(f"  ~ Recommended path absent: {r}")

    # Parse SKILL.md frontmatter
    skill_text = SKILL_SRC.joinpath("SKILL.md").read_text(encoding="utf-8")
    frontmatter_lines = [line for line in skill_text.split("\n")[1:10] if line.startswith("name:")]
    if not frontmatter_lines:
        errors.append("SKILL.md frontmatter missing 'name:' field")
    if "## Core Contract" not in skill_text:
        errors.append("SKILL.md missing 'Core Contract' section")

    # Validate route-registry.json if present
    reg_path = SKILL_SRC / "references" / "route-registry.json"
    if reg_path.is_file():
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        if "routes" not in reg:
            errors.append("route-registry.json missing 'routes' key")
        for route_id, entry in reg.get("routes", {}).items():
            if "family" not in entry:
                errors.append(f"route '{route_id}' missing 'family'")

    # Validate schema
    schema_path = SKILL_SRC / "schemas" / "study-package.schema.json"
    if schema_path.is_file():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if "required" not in schema:
            errors.append("study-package.schema.json missing 'required'")

    # Check for checklist files
    checklists_dir = SKILL_SRC / "references" / "checklists"
    if checklists_dir.is_dir():
        checklist_files = list(checklists_dir.glob("*.md"))
        if not checklist_files:
            errors.append("checklists/ directory is empty")
        elif verbose:
            print(f"  ✓ {len(checklist_files)} checklist files vendored")

    # Check for Python scripts
    script_files = list(SKILL_SRC.glob("scripts/*.py"))
    if not script_files:
        errors.append("scripts/ has no Python files")
    elif verbose:
        print(f"  ✓ {len(script_files)} Python scripts found")

    if errors:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ✘ {e}", file=sys.stderr)
        return 1

    print("SELF-TEST PASSED: all integrity checks OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install study-design-skills for multi-agent AI assistants."
    )
    parser.add_argument(
        "--target",
        choices=["all", "claude", "codex", "opencode", "openclaw", "hermes"],
        default="all",
        help="Which agent to install for (default: auto-detect installed)",
    )
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--self-test", action="store_true", help="Run integrity self-test")
    args = parser.parse_args()

    if args.self_test:
        return self_test(verbose=args.verbose)

    if args.target == "all":
        targets = detect_installed_agents()
        if not targets:
            print(
                "No agent config directories detected. Installing for all known targets.\n"
                "Run again with --target claude (or another) after the agent creates its config."
            )
            targets = list(AGENT_PATHS.keys())
    else:
        targets = [args.target]

    print(f"Installing {SKILL_NAME} for: {', '.join(targets)}\n")
    exit_code = 0
    for t in targets:
        code = install(t, verbose=args.verbose)
        if code != 0:
            exit_code = code
    if exit_code == 0:
        print(f"\nDone. Restart your agent, then use /{SKILL_NAME}.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())