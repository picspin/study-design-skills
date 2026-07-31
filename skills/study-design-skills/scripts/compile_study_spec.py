#!/usr/bin/env python3
"""Compile legacy or canonical study input into the versioned rendering contract."""

import argparse
import copy
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classify_study import DESIGNS, triage


REGISTRY_PATH = SCRIPT_DIR.parent / "references" / "route-registry.json"
SCHEMA_VERSION = "1.0"


STUDY_TYPE_PATTERNS = [
    ("controlled interrupted time series", "controlled_interrupted_time_series"),
    ("difference-in-differences", "difference_in_differences"),
    ("difference in differences", "difference_in_differences"),
    ("interrupted time series", "interrupted_time_series"),
    ("stepped-wedge", "stepped_wedge_cluster_rct"),
    ("stepped wedge", "stepped_wedge_cluster_rct"),
    ("comparative diagnostic", "comparative_diagnostic_accuracy"),
    ("diagnostic accuracy", "diagnostic_accuracy"),
    ("external validation", "prediction_model_validation"),
    ("prediction model", "prediction_model_development"),
    ("prognostic model", "prediction_model_development"),
    ("systematic review", "systematic_review_meta_analysis"),
    ("meta-analysis", "systematic_review_meta_analysis"),
    ("scoping review", "scoping_review"),
    ("randomized", "randomized_controlled_trial"),
    ("rct", "randomized_controlled_trial"),
    ("real-world evidence", "observational_causal"),
    ("comparative effectiveness", "observational_causal"),
    ("observational causal", "observational_causal"),
    ("cohort", "descriptive_observational"),
    ("observational", "descriptive_observational"),
    ("qualitative", "qualitative_study"),
    ("economic evaluation", "economic_evaluation")
]


def load_registry(path=REGISTRY_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def infer_design_id(spec):
    route = spec.get("route") or {}
    if route.get("design_id"):
        return route["design_id"], "canonical"
    if spec.get("confirmed_design"):
        return spec["confirmed_design"], "confirmed"
    study_type = str(spec.get("study_type") or "").strip().casefold()
    for pattern, design_id in STUDY_TYPE_PATTERNS:
        if pattern in study_type:
            return design_id, "study_type_inferred"
    proposal = spec.get("proposal")
    if proposal:
        result = triage(spec)
        if result.get("ready_for_design"):
            return result["recommended_design"]["design_id"], "triage_ready"
        if result.get("recommended_design"):
            return result["recommended_design"]["design_id"], "triage_unconfirmed"
    return "descriptive_observational", "fallback"


def default_title(spec, design_id):
    proposal = str(spec.get("proposal") or "").strip()
    if proposal:
        first = re.split(r"[。.!?！？\n]", proposal)[0].strip()
        if first:
            return first[:140]
    return DESIGNS[design_id]["label"]


def compile_spec(source, registry=None):
    """Return a canonical copy; never mutate the caller's object."""
    registry = registry or load_registry()
    spec = copy.deepcopy(source)
    design_id, resolution = infer_design_id(spec)
    routes = registry["routes"]
    if design_id not in DESIGNS or design_id not in routes:
        raise ValueError(f"Unknown confirmed_design '{design_id}'")
    design = DESIGNS[design_id]
    route = routes[design_id]

    spec["schema_version"] = SCHEMA_VERSION
    spec["confirmed_design"] = design_id
    spec["study_title"] = spec.get("study_title") or spec.get("title") or default_title(spec, design_id)
    spec["study_type"] = spec.get("study_type") or design["label"]
    spec["guideline_stack"] = spec.get("guideline_stack") or design["reporting"]
    spec["bias_tools"] = spec.get("bias_tools") or design["bias_tools"]
    spec["analysis_methods"] = spec.get("analysis_methods") or design["methods"]
    spec["table1_guidance"] = spec.get("table1_guidance") or design["table"]
    spec["flow_guidance"] = spec.get("flow_guidance") or design["flow"]
    spec["route"] = {
        "design_id": design_id,
        "family": route["family"],
        "label": design["label"],
        "flow_layout": route["flow_layout"],
        "table_profile": route["table_profile"],
        "references": route["references"],
        "rubric": route["rubric"],
        "required_content": route["required_content"],
        "forbidden_defaults": route["forbidden_defaults"],
        "resolution": resolution,
    }
    content_policy = {
        "profile": "clinical_concise",
        "paragraph_max_sentences": 3,
        "bullet_max_words": 18,
        "table_cell_max_words": 25,
        "parallel_content": "Use one comparison table; rows are stages or domains and columns are groups, periods, models, or analysis sets.",
    }
    content_policy.update(spec.get("content_policy") or {})
    spec["content_policy"] = content_policy

    external_evidence = {
        "activation": "disabled",
        "allow_external_context": False,
        "requested_providers": [],
        "retrievals": [],
    }
    external_evidence.update(spec.get("external_evidence") or {})
    spec["external_evidence"] = external_evidence

    provenance = dict(spec.get("provenance") or {})
    provenance.update({
        "compiler": "study-design-skills/compile_study_spec.py",
        "registry_version": registry["registry_version"],
        "source_format": "canonical" if source.get("schema_version") else "legacy_flat_json",
    })
    spec["provenance"] = provenance
    return spec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    compiled = compile_spec(json.loads(args.spec.read_text(encoding="utf-8")))
    payload = json.dumps(compiled, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
