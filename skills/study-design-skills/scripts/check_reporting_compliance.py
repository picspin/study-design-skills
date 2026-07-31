#!/usr/bin/env python3
"""Reporting compliance auditor — route-guided EQUATOR audit for any study design.

Usage:
  python scripts/check_reporting_compliance.py study-package.json manuscript.md --out report.md
  python scripts/check_reporting_compliance.py study-package.json manuscript.md --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKLIST_DIR = SCRIPT_DIR.parent / "references" / "checklists"
REGISTRY_PATH = SCRIPT_DIR.parent / "references" / "route-registry.json"

# Design → guideline mapping (mirrors route-registry.json)
ROUTE_TO_GUIDELINE: dict[str, str] = {
    "randomized_controlled_trial": "CONSORT",
    "stepped_wedge_cluster_rct": "CONSORT",
    "controlled_interrupted_time_series": "TREND",
    "interrupted_time_series": "TREND",
    "difference_in_differences": "TREND",
    "observational_causal": "STROBE",
    "descriptive_observational": "STROBE",
    "diagnostic_accuracy": "STARD",
    "comparative_diagnostic_accuracy": "STARD",
    "prediction_model_development": "TRIPOD+AI",
    "prediction_model_validation": "TRIPOD+AI",
    "systematic_review_meta_analysis": "PRISMA",
    "systematic_review_narrative": "PRISMA",
    "scoping_review": "PRISMA",
    "qualitative_study": "SRQR",
    "economic_evaluation": "CHEERS",
}

DESIGN_FAMILY_GUIDELINE: dict[str, str] = {
    "randomized_trial": "CONSORT",
    "time_series_qi": "TREND",
    "causal_observational": "STROBE",
    "descriptive_observational": "STROBE",
    "diagnostic_accuracy": "STARD",
    "prediction": "TRIPOD+AI",
    "evidence_synthesis": "PRISMA",
    "qualitative": "SRQR",
    "economic": "CHEERS",
}


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def load_study_package(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_guideline(study_package: dict) -> str:
    """Return the primary guideline acronym based on study package's route."""
    design = study_package.get("confirmed_design", "")
    family = study_package.get("route", {}).get("family", "")

    if design in ROUTE_TO_GUIDELINE:
        return ROUTE_TO_GUIDELINE[design]
    if family in DESIGN_FAMILY_GUIDELINE:
        return DESIGN_FAMILY_GUIDELINE[family]
    return "CONSORT"  # fallback


def checklist_items(filename: str) -> list[dict]:
    """Parse a checklist markdown file and extract items."""
    path = CHECKLIST_DIR / filename
    if not path.is_file():
        print(f"  MISSING_CHECKLIST: {path}", file=sys.stderr)
        return []

    text = path.read_text(encoding="utf-8")
    items = []
    in_table = False
    for line in text.split("\n"):
        # Detect table rows
        if line.startswith("| ") and "|" in line[2:]:
            cells = [c.strip() for c in line.split("|")]
            # Skip header / separator rows
            if any(c in ("---", ":", "") for c in cells[1:-1]):
                continue
            if len(cells) >= 4:
                item = {
                    "number": cells[1],
                    "section": cells[2] if len(cells) > 2 else "",
                    "description": cells[3] if len(cells) > 3 else "",
                }
                items.append(item)
        elif line.startswith("## "):
            in_table = False
        elif line.startswith("| # ") or line.startswith("|#"):
            in_table = True
    return items


def scan_manuscript(manuscript_path: Path, items: list[dict]) -> list[dict]:
    """Scan manuscript for each checklist item and assign a status."""
    if not manuscript_path.is_file():
        return [dict(item, status="NOT_SCANNED", location="", notes="Manuscript file not found")
                for item in items]

    text = manuscript_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    assessed = []
    for item in items:
        search_terms = item.get("description", "")[:80].strip()
        if not search_terms:
            assessed.append(dict(item, status="NI", location="", notes="No searchable description"))
            continue

        # Simple keyword matching — extended logic could use embedding search
        found_lines = []
        for i, line in enumerate(lines, 1):
            if any(word.lower() in line.lower() for word in search_terms.split()[:5]):
                found_lines.append(i)
                if len(found_lines) >= 3:
                    break

        if found_lines:
            status = "PRESENT"
            location = f"Lines {found_lines[0]}-{found_lines[-1]}"
            notes = f"Found {len(found_lines)} mention(s)"
        else:
            status = "MISSING"
            location = ""
            notes = "Not found in manuscript"

        assessed.append(dict(item, status=status, location=location, notes=notes))

    return assessed


def generate_report(
    study_package: dict,
    checklist_items: list[dict],
    assessments: list[dict],
    guideline: str,
) -> str:
    """Generate structured compliance report."""
    present = sum(1 for a in assessments if a["status"] == "PRESENT")
    missing = sum(1 for a in assessments if a["status"] == "MISSING")
    partial = sum(1 for a in assessments if a["status"] == "PARTIAL")
    na = sum(1 for a in assessments if a["status"] in ("N/A", "NI", "NOT_SCANNED"))
    applicable = len(assessments) - na
    compliance = round(present / applicable * 100, 1) if applicable > 0 else 0

    lines = [
        "---",
        f"# Reporting Compliance Report",
        "",
        f"**Study:** {study_package.get('study_title', 'Untitled')}",
        f"**Guideline:** {guideline}",
        f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
        f"**Assessed by:** study-design-skills (deterministic pre-screening)",
        "",
        "## Summary",
        "",
        f"| Status | Count | % |",
        f"|--------|-------|---|",
        f"| PRESENT | {present} | {round(present/len(assessments)*100,1) if assessments else 0} |",
        f"| PARTIAL | {partial} | {round(partial/len(assessments)*100,1) if assessments else 0} |",
        f"| MISSING | {missing} | {round(missing/len(assessments)*100,1) if assessments else 0} |",
        f"| N/A | {na} | {round(na/len(assessments)*100,1) if assessments else 0} |",
        f"| **Total** | **{len(assessments)}** | **100** |",
        "",
        f"**Overall compliance:** {present}/{applicable} ({compliance}%)",
        "",
        "## Item-by-Item Checklist",
        "",
        "| # | Item | Status | Location | Notes |",
        "|---|------|--------|----------|-------|",
    ]

    for a in assessments:
        lines.append(
            f"| {a.get('number', '')} | {a.get('description', '')[:60]} | "
            f"{a['status']} | {a.get('location', '')} | {a.get('notes', '')} |"
        )

    lines.extend([
        "",
        "## Action Items (Priority Order)",
        "",
    ])

    for a in assessments:
        if a["status"] == "MISSING":
            lines.append(f"1. **[MISSING]** Item {a.get('number', '')}: {a.get('description', '')[:80]}")
            lines.append(f"   - Suggested location: Methods section")
            lines.append(f"   - Suggested fix: Add description of {a.get('description', '')[:60]}")
        elif a["status"] == "PARTIAL":
            lines.append(f"2. **[PARTIAL]** Item {a.get('number', '')}: {a.get('description', '')[:80]}")
            lines.append(f"   - Current: {a.get('notes', '')}")
            lines.append(f"   - Needed: Additional detail")

    lines.extend([
        "",
        "---",
        "**Note:** This is a deterministic pre-screening aid. Final compliance should be verified",
        "by all co-authors and ideally by a methodologist.",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="EQUATOR reporting compliance audit")
    parser.add_argument("study_package", type=Path, help="Compiled study-package.json")
    parser.add_argument("manuscript", type=Path, nargs="?", help="Manuscript file (optional)")
    parser.add_argument("--out", type=Path, help="Output report path")
    parser.add_argument("--json", action="store_true", help="Output JSON summary to stderr")
    parser.add_argument("--guideline", "-g", help="Override guideline auto-selection")
    args = parser.parse_args()

    # Load package
    try:
        pkg = load_study_package(args.study_package)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    guideline = args.guideline or resolve_guideline(pkg)
    print(f"  Resolved guideline: {guideline}", file=sys.stderr)

    # Resolve checklist file
    checklist_file = guideline.replace("-", "_").replace("+", "PLUS").upper()
    checklist_path = CHECKLIST_DIR / f"{checklist_file}.md"
    # Try common patterns
    if not checklist_path.is_file():
        alt_map = {
            "CONSORT": "CONSORT_2025",
            "TRIPOD+AI": "TRIPOD_AI",
            "TRIPODPLUSAI": "TRIPOD_AI",
            "PRISMA": "PRISMA_2020",
        }
        alt = alt_map.get(checklist_file)
        if alt:
            checklist_path = CHECKLIST_DIR / f"{alt}.md"
    if not checklist_path.is_file():
        print(f"  ERROR: checklist not found for {guideline} at {checklist_path}", file=sys.stderr)
        return 1

    items = checklist_items(checklist_path.name)
    if not items:
        print(f"  WARNING: no parsable items found in {checklist_path.name}", file=sys.stderr)
    else:
        print(f"  Loaded {len(items)} checklist items from {checklist_path.name}", file=sys.stderr)

    # Scan manuscript
    assessments = []
    if args.manuscript:
        assessments = scan_manuscript(args.manuscript, items)
    else:
        assessments = [dict(item, status="NOT_SCANNED", location="", notes="No manuscript provided")
                       for item in items]

    report = generate_report(pkg, items, assessments, guideline)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"  Report written to {args.out}", file=sys.stderr)
    else:
        print(report)

    if args.json:
        summary = {
            "guideline": guideline,
            "checklist_file": str(checklist_path),
            "total_items": len(items),
            "present": sum(1 for a in assessments if a["status"] == "PRESENT"),
            "partial": sum(1 for a in assessments if a["status"] == "PARTIAL"),
            "missing": sum(1 for a in assessments if a["status"] == "MISSING"),
            "na": sum(1 for a in assessments if a["status"] in ("N/A", "NI", "NOT_SCANNED")),
            "action_items": [{"item_number": a.get("number"), "item_name": a.get("description", "")[:60],
                              "status": a["status"], "suggested_fix": f"Add {a.get('description', '')[:60]}"}
                             for a in assessments if a["status"] in ("MISSING", "PARTIAL")],
        }
        print(json.dumps(summary, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())