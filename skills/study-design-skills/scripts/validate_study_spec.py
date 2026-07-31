#!/usr/bin/env python3
"""Validate the canonical study contract and clinical-density rules."""

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compile_study_spec import compile_spec

SCHEMA_PATH = SCRIPT_DIR.parent / "schemas" / "study-package.schema.json"


def text_units(value):
    text = str(value or "")
    latin_words = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))
    cjk_chars = len(re.findall(r"[\u3400-\u9fff]", text))
    return latin_words + (cjk_chars + 1) // 2


def sentence_count(value):
    return len([part for part in re.split(r"[.!?。！？]+", str(value or "")) if part.strip()])


def add_issue(items, code, path, message, severity="warning"):
    items.append({"code": code, "path": path, "severity": severity, "message": message})


def validate_spec(source, strict=False):
    spec = compile_spec(source)
    issues = []
    route = spec["route"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for error in sorted(Draft202012Validator(schema).iter_errors(spec), key=lambda item: list(item.path)):
        path = ".".join(str(part) for part in error.path) or "$"
        add_issue(issues, "schema", path, error.message, "error")

    for field in ["study_title", "study_type", "confirmed_design", "route"]:
        if not spec.get(field):
            add_issue(issues, "required", field, f"{field} is required.", "error")

    for field in route.get("required_content", []):
        if spec.get(field) in [None, "", [], {}]:
            severity = "error" if strict else "warning"
            add_issue(issues, "route_required", field, f"{route['label']} requires explicit content for '{field}'.", severity)

    primary = spec.get("primary_objective")
    if primary and text_units(primary) > 45:
        add_issue(issues, "density_primary", "primary_objective", "Primary objective exceeds 45 readable units; keep one estimand and move detail to structured fields.")

    secondary = spec.get("secondary_objectives") or []
    if isinstance(secondary, str):
        secondary = [secondary]
    for index, item in enumerate(secondary):
        if text_units(item) > 35:
            add_issue(issues, "density_secondary", f"secondary_objectives[{index}]", "Secondary objective is too dense; split endpoint, population, and analysis method.")

    notes = spec.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    for index, note in enumerate(notes):
        if sentence_count(note) > 3 or text_units(note) > 80:
            add_issue(issues, "density_note", f"notes[{index}]", "Narrative note exceeds three sentences or 80 readable units; convert parallel content to a table or bullets.")

    for index, group in enumerate(spec.get("groups") or []):
        label = group.get("label") if isinstance(group, dict) else group
        if text_units(label) > 16:
            add_issue(issues, "density_group", f"groups[{index}]", "Group label is too long for Table 1 and flowchart headers.")

    for index, variable in enumerate(spec.get("variables") or []):
        label = variable.get("label", variable.get("name", "")) if isinstance(variable, dict) else variable
        if text_units(label) > 18:
            add_issue(issues, "density_variable", f"variables[{index}]", "Variable label is too long; put definitions in footnotes.")

    exclusions = spec.get("flow_exclusions") or {}
    for key, reasons in exclusions.items():
        reasons = [reasons] if isinstance(reasons, str) else reasons
        for index, reason in enumerate(reasons or []):
            if text_units(reason) > 25:
                add_issue(issues, "density_flow", f"flow_exclusions.{key}[{index}]", "Flowchart reason exceeds 25 readable units; shorten the node and move detail to the caption.")

    external = spec.get("external_evidence") or {}
    if external.get("retrievals") and external.get("activation") == "disabled":
        add_issue(issues, "external_evidence_policy", "external_evidence.activation", "External retrievals are present while external evidence is disabled.", "error")

    if spec.get("include_p_values") and route["family"] == "randomized_trial":
        add_issue(issues, "method_mismatch", "include_p_values", "Randomized-trial Table 1 should not use baseline p values by default.", "error" if strict else "warning")
    if spec.get("matching") and route["family"] in {"randomized_trial", "prediction", "diagnostic_accuracy", "time_series_qi"}:
        add_issue(issues, "method_mismatch", "matching", f"Matching is not a default bias-control method for {route['family']}.")

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    return {
        "valid": not errors,
        "schema_version": spec["schema_version"],
        "route": route,
        "errors": errors,
        "warnings": warnings,
        "compiled_spec": spec,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate_spec(json.loads(args.spec.read_text(encoding="utf-8")), strict=args.strict)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload)
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
