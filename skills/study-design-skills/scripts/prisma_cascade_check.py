#!/usr/bin/env python3
"""PRISMA 2020 flow-diagram arithmetic auto-verify.

Checks the four arithmetic equations and two cross-references defined
in SKILL.md Step 4d. Exit 0 = all pass, 1 = at least one failure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_arithmetic(
    identified: int,
    duplicates: int,
    screened: int,
    screened_excluded: int,
    sought: int,
    not_retrieved: int,
    assessed: int,
    assessed_excluded: int,
    included: int,
) -> list[str]:
    errors = []

    # eq 1
    if screened != identified - duplicates:
        errors.append(f"EQ1: screened ({screened}) ≠ identified ({identified}) − duplicates ({duplicates}) = {identified - duplicates}")
    # eq 2
    if sought != screened - screened_excluded:
        errors.append(f"EQ2: sought ({sought}) ≠ screened ({screened}) − excluded at screening ({screened_excluded}) = {screened - screened_excluded}")
    # eq 3
    if assessed != sought - not_retrieved:
        errors.append(f"EQ3: assessed ({assessed}) ≠ sought ({sought}) − not retrieved ({not_retrieved}) = {sought - not_retrieved}")
    # eq 4
    if included != assessed - assessed_excluded:
        errors.append(f"EQ4: included ({included}) ≠ assessed ({assessed}) − excluded ({assessed_excluded}) = {assessed - assessed_excluded}")

    return errors


def check_cross_reference(text_counts: dict[str, int], fig_counts: dict[str, int]) -> list[str]:
    errors = []
    for key in set(text_counts) | set(fig_counts):
        if text_counts.get(key) != fig_counts.get(key):
            errors.append(f"XREF:{key}: text says {text_counts.get(key, '?')}, figure says {fig_counts.get(key, '?')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA flow arithmetic auto-verify")
    parser.add_argument("--identified", type=int, required=True)
    parser.add_argument("--duplicates", type=int, default=0)
    parser.add_argument("--screened", type=int, required=True)
    parser.add_argument("--screened-excluded", type=int, default=0)
    parser.add_argument("--sought", type=int, required=True)
    parser.add_argument("--not-retrieved", type=int, default=0)
    parser.add_argument("--assessed", type=int, required=True)
    parser.add_argument("--assessed-excluded", type=int, default=0)
    parser.add_argument("--included", type=int, required=True)
    parser.add_argument("--text-counts", help="JSON: text->{key:int}")
    parser.add_argument("--fig-counts", help="JSON: fig->{key:int}")
    parser.add_argument("--out", type=Path, help="Write audit JSON to file")
    args = parser.parse_args()

    arithmetic_errors = check_arithmetic(
        args.identified, args.duplicates, args.screened,
        args.screened_excluded, args.sought, args.not_retrieved,
        args.assessed, args.assessed_excluded, args.included,
    )

    xref_errors = []
    if args.text_counts and args.fig_counts:
        text = json.loads(args.text_counts)
        fig = json.loads(args.fig_counts)
        xref_errors = check_cross_reference(text, fig)

    all_errors = arithmetic_errors + xref_errors
    passed = len(all_errors) == 0

    result = {
        "passed": passed,
        "arithmetic_checks": {
            "eq1_screening": {"numeric": args.identified - args.duplicates, "claim": args.screened, "ok": args.screened == args.identified - args.duplicates},
            "eq2_sought": {"numeric": args.screened - args.screened_excluded, "claim": args.sought, "ok": args.sought == args.screened - args.screened_excluded},
            "eq3_assessed": {"numeric": args.sought - args.not_retrieved, "claim": args.assessed, "ok": args.assessed == args.sought - args.not_retrieved},
            "eq4_included": {"numeric": args.assessed - args.assessed_excluded, "claim": args.included, "ok": args.included == args.assessed - args.assessed_excluded},
        },
        "cross_reference_errors": xref_errors,
        "errors": all_errors,
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if all_errors:
        print(f"PRISMA AUDIT FAILED — {len(all_errors)} error(s):", file=sys.stderr)
        for e in all_errors:
            print(f"  ✘ {e}", file=sys.stderr)
        return 1
    else:
        print("PRISMA AUDIT PASSED — all arithmetic and cross-references agree.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())