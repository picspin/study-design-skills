#!/usr/bin/env python3
"""Optional TypeSafe/Jev judgments for study routing and benchmark calibration."""

import argparse
import json
import os
from pathlib import Path
from urllib import request

from classify_study import DESIGNS, triage
from compile_study_spec import compile_spec
from design_study import score_study_design


API_URL = "https://api.typesafe.ai/v1/systemone"
LEVELS = [
    "No source evidence or a clear mismatch.",
    "A relevant idea is present, but major design information is missing.",
    "The essential design information is specified; important uncertainties remain.",
    "The design is well supported and most operational details are documented.",
    "The source and artifact give complete, internally consistent evidence suitable for independent review.",
]
SCORE_DIMENSIONS = {
    "question_design_fit": "How well does the confirmed study design answer the stated primary scientific question?",
    "reporting_fit": "How well do the selected reporting statements and bias controls fit this design?",
    "artifact_coherence": "How well do the source denominators, Table 1, study flow, outcome, and analysis plan agree?",
    "journal_fit": "How well does the study's evidence and clinical relevance meet the stated target journal scope?",
}


def request_jev(payload, transport=None):
    if transport is not None:
        return transport(payload)
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise RuntimeError("TYPESAFE_API_KEY is not set")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        API_URL,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        return json.load(response)


def route_judgment(source, transport=None):
    state = {
        "proposal": source.get("proposal") or source.get("research_question") or source.get("study_title") or "",
        "primary_objective": source.get("primary_objective") or "",
        "data_source": source.get("data_source") or "",
        "allocation": source.get("allocation") or "",
        "comparator": source.get("comparator") or "",
        "analysis_unit": source.get("analysis_unit") or "",
    }
    questions = {
        "study_design": {
            "type": "choice",
            "instructions": "Choose the design best supported by the supplied scientific aim, sampling, allocation, comparator, and timing. Do not infer an intervention or causal contrast from a descriptive survey.",
            "criteria": {key: value["label"] + ". " + value["flow"] for key, value in DESIGNS.items()}
            | {
                "insufficient_information": "The study aim or design-defining information is insufficient; ask a clarifying question.",
                "outside_current_registry": "The scientific study is sufficiently described but its design is outside the current biomedical route registry; identify the applicable statement before extending the registry.",
            },
        }
    }
    result = request_jev({"model": "jev-latest", "state": state, "questions": questions}, transport)
    answer = result["answers"]["study_design"]
    if answer.get("type") != "choice" or answer.get("choice") not in questions["study_design"]["criteria"]:
        raise ValueError("Jev returned an invalid study-design choice")
    probabilities = answer.get("probabilities") or {}
    ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    deterministic = triage(source)
    confirmed = source.get("confirmed_design")
    selected = confirmed if confirmed in DESIGNS else deterministic["recommended_design"]["design_id"]
    return {
        "model": result.get("model", "unknown"),
        "choice": answer["choice"],
        "confidence": answer.get("confidence"),
        "probabilities": probabilities,
        "top_two": ranked[:2],
        "selected_design": selected,
        "status": "confirmed_design_preserved" if confirmed in DESIGNS else "advisory_only",
        "needs_clarification": answer["choice"] == "insufficient_information" or float(answer.get("confidence", 0)) < 0.55,
        "needs_route_extension": answer["choice"] == "outside_current_registry",
        "rule_stage": deterministic["stage"],
    }


def benchmark_judgment(source, transport=None):
    spec = compile_spec(source)
    _, rule_score, _, blockers, _, _ = score_study_design(spec)
    state = {
        "primary_objective": spec.get("primary_objective"),
        "study_type": spec.get("study_type"),
        "confirmed_design": spec.get("confirmed_design"),
        "population": spec.get("population"),
        "comparator": spec.get("comparator"),
        "guideline_stack": spec.get("guideline_stack"),
        "flow_counts": spec.get("flow_counts"),
        "flow_exclusions": spec.get("flow_exclusions"),
        "table1_headings": [row.get("characteristic") for row in (spec.get("precomputed_table_rows") or [])[:35]],
        "sample_size": spec.get("sample_size"),
        "analysis_plan": spec.get("analysis_plan"),
        "bias_control": spec.get("bias_control"),
        "unresolved_assumptions": spec.get("notes"),
        "target_jcr_category": spec.get("target_jcr_category"),
    }
    questions = {
        key: {"type": "score", "instructions": instruction, "criteria": LEVELS}
        for key, instruction in SCORE_DIMENSIONS.items()
    }
    result = request_jev({"model": "jev-latest", "state": state, "questions": questions}, transport)
    dimensions = {}
    for key in questions:
        answer = result["answers"][key]
        if answer.get("type") != "score" or not 0 <= float(answer.get("score", -1)) <= 4:
            raise ValueError(f"Jev returned an invalid score for {key}")
        dimensions[key] = {
            "score_0_to_4": round(float(answer["score"]), 3),
            "confidence": answer.get("confidence"),
            "probabilities": answer.get("probabilities"),
        }
    jev_score = round(sum(item["score_0_to_4"] for item in dimensions.values()) / 4 * 2.5, 2)
    return {
        "model": result.get("model", "unknown"),
        "dimensions": dimensions,
        "jev_score_10": jev_score,
        "rule_score_10": rule_score,
        "rule_blockers": blockers,
        "combination": "0.8 * rule_score + 0.2 * Jev_score, subject to existing rule-based caps",
        "status": "completed",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--mode", choices=["route", "benchmark", "both"], default="both")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    source = json.loads(args.spec.read_text(encoding="utf-8"))
    result = {}
    if args.mode in {"route", "both"}:
        result["route"] = route_judgment(source)
    if args.mode in {"benchmark", "both"}:
        result["benchmark"] = benchmark_judgment(source)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
