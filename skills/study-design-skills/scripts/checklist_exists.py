#!/usr/bin/env python3
"""Deterministic checklist existence guard — fail-fast if vendored file is missing.

Exit codes:
  0 → checklist exists
  1 → MISSING_CHECKLIST_CONTRACT_VIOLATION (file not found)
  2 → UNKNOWN_GUIDELINE (no name mapping)

This guard enforces the contract: never silently construct a checklist from
model memory. A from-memory audit is permitted ONLY with --allow-from-memory,
and the resulting report must carry a NON-AUTHORITATIVE banner.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKLIST_DIR = SCRIPT_DIR.parent / "references" / "checklists"

# Canonical name → expected file mapping
GUIDELINE_FILES: dict[str, str] = {
    # Clinical epidemiology
    "CONSORT": "CONSORT_2025.md",
    "CONSORT-AI": "CONSORT_AI.md",
    "CONSORT_AI": "CONSORT_AI.md",
    "STROBE": "STROBE.md",
    "RECORD": "RECORD.md",
    "STARD": "STARD.md",
    "STARD-AI": "STARD_AI.md",
    "STARD_AI": "STARD_AI.md",
    "TRIPOD": "TRIPOD.md",
    "TRIPOD-AI": "TRIPOD_AI.md",
    "TRIPOD+AI": "TRIPOD_AI.md",
    "TRIPOD_AI": "TRIPOD_AI.md",
    "PRISMA": "PRISMA_2020.md",
    "PRISMA-DTA": "PRISMA_DTA.md",
    "PRISMA_2020": "PRISMA_2020.md",
    "SQUIRE": "SQUIRE_2.md",
    "SQUIRE_2": "SQUIRE_2.md",
    "TREND": "TREND.md",
    "CHEERS": "CHEERS.md",
    "SRQR": "SRQR.md",
    "COREQ": "COREQ.md",
    "ARRIVE": "ARRIVE_2.md",
    "ARRIVE_2": "ARRIVE_2.md",
    "CARE": "CARE.md",
    "SPIRIT": "SPIRIT.md",
    "CLAIM": "CLAIM_2024.md",
    "CLAIM_2024": "CLAIM_2024.md",
    "MI-CLEAR-LLM": "MI_CLEAR_LLM.md",
    "MI_CLEAR_LLM": "MI_CLEAR_LLM.md",
    # Risk of bias tools
    "ROB-2": "ROB_2.md",
    "ROB_2": "ROB_2.md",
    "RoB2": "ROB_2.md",
    "ROBINS-I": "ROBINS_I.md",
    "ROBINS_I": "ROBINS_I.md",
    "QUADAS-3": "QUADAS_3.md",
    "QUADAS_3": "QUADAS_3.md",
    "QUADAS-C": "QUADAS_C.md",
    "QUADAS_C": "QUADAS_C.md",
    "PROBAST": "PROBAST_AI.md",
    "PROBAST-AI": "PROBAST_AI.md",
    "PROBAST+AI": "PROBAST_AI.md",
    "PROBAST_AI": "PROBAST_AI.md",
    "ROB-ME": "ROB_ME.md",
    "ROB_ME": "ROB_ME.md",
    "ROB-NMA": "ROB_NMA.md",
    "ROB_NMA": "ROB_NMA.md",
}


def resolve_file(guideline: str) -> Path | None:
    norm = guideline.replace("-", "_").upper()
    # Try exact match first, then case-insensitive
    for key, filename in GUIDELINE_FILES.items():
        if key.replace("-", "_").upper() == norm:
            return CHECKLIST_DIR / filename
    # Fall back to treating input as a filename directly
    candidate = CHECKLIST_DIR / guideline
    if candidate.suffix.lower() != ".md":
        candidate = candidate.with_suffix(".md")
    if candidate.is_file():
        return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic checklist existence guard."
    )
    parser.add_argument("--guideline", "-g", required=True, help="Guideline acronym or alias")
    parser.add_argument("--allow-from-memory", action="store_true",
                        help="Skip guard and permit non-authoritative audit")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.allow_from_memory:
        print(f"WARNING: --allow-from-memory used. Checklist will be NON-AUTHORITATIVE.\n"
              f"There is no vendored file for {args.guideline}. Assessment is constructed\n"
              f"from model knowledge and should NOT be marked as submission-ready.\n",
              file=sys.stderr)
        return 0

    checklist_path = resolve_file(args.guideline)
    if checklist_path is None:
        print(f"UNKNOWN_GUIDELINE: '{args.guideline}' is not a recognised guideline acronym.\n"
              f"Known: {', '.join(sorted(GUIDELINE_FILES))}",
              file=sys.stderr)
        return 2

    if checklist_path.is_file():
        if args.verbose:
            print(f"✓ {args.guideline} -> {checklist_path}")
        return 0

    print(f"MISSING_CHECKLIST_CONTRACT_VIOLATION\n"
          f"Guideline '{args.guideline}' resolved to {checklist_path} but the file does\n"
          f"not exist. Do not construct checklist items from memory.\n"
          f"Use --allow-from-memory only if the user explicitly accepts a non-authoritative audit.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())