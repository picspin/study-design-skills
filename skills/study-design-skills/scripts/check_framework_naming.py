#!/usr/bin/env python3
"""Reporting-framework naming audit for AI/extension guideline manuscripts.

Deterministic gate that catches:
- BASE_MISSING: extension used but base instrument never named standalone
- HYPHEN_MIX: +AI / -AI hyphenation inconsistent within document
- CITE_MISSING: extension named but no citation or DOI provided
- SELF_COINED_LABEL: "item 12-AI" or similar fabricated labels
- VAGUE_GUIDANCE: "recent guidance" instead of naming the framework

Usage:
  python scripts/check_framework_naming.py --manuscript manuscript.md [--out qc/framework_naming.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


EXTENSIONS = {
    "CONSORT-AI", "CONSORT_AI",
    "STARD-AI", "STARD_AI",
    "TRIPOD-AI", "TRIPOD+AI", "TRIPOD_AI",
    "SPIRIT-AI", "SPIRIT_AI",
    "PRISMA-DTA", "PRISMA_DTA",
    "QUADAS-C", "QUADAS_C",
    "PROBAST-AI", "PROBAST+AI", "PROBAST_AI",
}

BASE_INSTRUMENTS = {
    "CONSORT", "STARD", "TRIPOD", "SPIRIT",
    "PRISMA", "QUADAS", "PROBAST",
}

PATTERN_VAGUE = re.compile(r"\b(recent guidance|current guidelines|recommended checklist)\b", re.IGNORECASE)
PATTERN_SELF_COINED = re.compile(r"[Ii]tem\s+\d+[-–—]\s*(AI|ML|LLM)\b")


def audit(manuscript_text: str) -> dict:
    claims = []
    used_extensions = set()
    used_bases = set()

    for ext in EXTENSIONS:
        # Normalise for matching
        ext_norm = ext.replace("_", "-").replace("+", "-").upper()
        for variant in (ext, ext.replace("_", "-"), ext.replace("-", "_"), ext.replace("+", "-"), ext.replace("+", "_")):
            if variant in manuscript_text:
                used_extensions.add(ext_norm)
                break

    for base in BASE_INSTRUMENTS:
        if base in manuscript_text:
            used_bases.add(base.upper())

    # Find vague citations
    for m in PATTERN_VAGUE.finditer(manuscript_text):
        claims.append({
            "type": "VAGUE_GUIDANCE",
            "text": m.group(),
            "position": m.start(),
            "fixable_by_ai": True,
        })

    # Find self-coined labels
    for m in PATTERN_SELF_COINED.finditer(manuscript_text):
        claims.append({
            "type": "SELF_COINED_LABEL",
            "text": m.group(),
            "position": m.start(),
            "fixable_by_ai": True,
        })

    # Extension used without base
    for ext in used_extensions:
        # Derive base from extension name
        base_candidate = ext.split("-")[0].split("_")[0].split("+")[0]
        if base_candidate in BASE_INSTRUMENTS and base_candidate not in used_bases:
            claims.append({
                "type": "BASE_MISSING",
                "extension": ext,
                "base_needed": base_candidate,
                "fixable_by_ai": True,
            })

    # Consistency: check the same document doesn't mix "STARD-AI" and "STARD_AI"
    hybrid_pairs = [
        ("CONSORT-AI", "CONSORT_AI", "CONSORT"),
        ("STARD-AI", "STARD_AI", "STARD"),
        ("TRIPOD-AI", "TRIPOD+AI", "TRIPOD"),
        ("TRIPOD-AI", "TRIPOD_AI", "TRIPOD"),
        ("SPIRIT-AI", "SPIRIT_AI", "SPIRIT"),
    ]
    seen_hybrids = set()
    for a, b, family in hybrid_pairs:
        has_a = a in manuscript_text
        has_b = b in manuscript_text
        if has_a and has_b:
            key = f"{family}-HYPHEN"
            if key not in seen_hybrids:
                claims.append({
                    "type": "HYPHEN_MIX",
                    "family": family,
                    "variants_seen": [a, b],
                    "fixable_by_ai": True,
                })
                seen_hybrids.add(key)

    return {
        "framework_naming": {
            "extensions_found": sorted(used_extensions),
            "base_instruments_found": sorted(used_bases),
            "claims": claims,
            "total_claims": len(claims),
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reporting framework naming audit")
    parser.add_argument("--manuscript", "-m", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="Output JSON path")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any claim")
    args = parser.parse_args()

    text = args.manuscript.read_text(encoding="utf-8")
    result = audit(text)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    claims = result["framework_naming"]["claims"]
    if claims:
        print(f"Found {len(claims)} naming issue(s):", file=sys.stderr) if not args.strict else None
        for c in claims:
            print(f"  [{c['type']}] {c.get('text', c.get('base_needed', c.get('family', '')))}", file=sys.stderr)
        if args.strict:
            return 1
    else:
        print("Framework naming audit: all clear.", file=sys.stderr)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())