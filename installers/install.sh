#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="study-design-skills"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_SRC="${REPO_DIR}/skills/${SKILL_NAME}"

# Agent targets — expand as needed
declare -A AGENT_DIRS
AGENT_DIRS[claude]="${HOME}/.claude/skills"
AGENT_DIRS[codex]="${HOME}/.codex/skills"
AGENT_DIRS[opencode]="${HOME}/.opencode/skills"
AGENT_DIRS[openclaw]="${HOME}/.openclaw/skills"
AGENT_DIRS[hermes]="${HOME}/.hermes/skills"

usage() {
  echo "Usage: $0 [--target all|claude|codex|opencode|openclaw|hermes] [--verbose]" >&2
  exit 1
}

TARGET="all"
VERBOSE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --verbose) VERBOSE=true; shift ;;
    *) usage ;;
  esac
done

if [[ ! -d "${SKILL_SRC}" ]]; then
  echo "ERROR: source skill directory not found: ${SKILL_SRC}" >&2
  exit 1
fi
if [[ ! -f "${SKILL_SRC}/SKILL.md" ]]; then
  echo "ERROR: ${SKILL_SRC}/SKILL.md not found" >&2
  exit 1
fi

install_for_agent() {
  local agent="$1"
  local dest="${AGENT_DIRS[$agent]:-}"
  if [[ -z "$dest" ]]; then
    echo "  ~ ${agent}: unknown target, skipping"
    return
  fi
  mkdir -p "${dest}"
  local target_dir="${dest}/${SKILL_NAME}"
  if [[ -d "${target_dir}" ]]; then
    rm -rf "${target_dir}"
  fi
  cp -r "${SKILL_SRC}" "${target_dir}"
  if [[ ! -f "${target_dir}/SKILL.md" ]]; then
    echo "  ✘ ${agent}: FAILED (SKILL.md not found after copy)" >&2
    return 1
  fi
  $VERBOSE && echo "  ✔ ${agent}: installed -> ${target_dir}"
  return 0
}

if [[ "$TARGET" == "all" ]]; then
  agents=()
  for a in "${!AGENT_DIRS[@]}"; do
    if [[ -d "${AGENT_DIRS[$a]%/*}" ]]; then
      agents+=("$a")
    fi
  done
  if [[ ${#agents[@]} -eq 0 ]]; then
    echo "No agent config directories detected. Installing for all known targets."
    agents=("${!AGENT_DIRS[@]}")
  fi
else
  agents=("$TARGET")
fi

echo "Installing ${SKILL_NAME} for: ${agents[*]}"
failed=0
for a in "${agents[@]}"; do
  install_for_agent "$a" || failed=1
done

if [[ $failed -eq 0 ]]; then
  echo "Done. Restart your agent, then use /${SKILL_NAME}."
fi
exit $failed