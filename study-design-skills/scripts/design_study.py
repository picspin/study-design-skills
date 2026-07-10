#!/usr/bin/env python3
"""Generate a study design memo or a multi-format study design package.

Input: JSON study specification.
Output: Markdown, or CSV/XLSX/HTML/Markdown when --out-dir is supplied.
"""

import argparse
import json
from pathlib import Path


GUIDELINES = {
    "rct": "CONSORT 2025 or applicable CONSORT extension",
    "randomized trial": "CONSORT 2025 or applicable CONSORT extension",
    "clinical trial": "CONSORT 2025 or applicable CONSORT extension",
    "protocol": "SPIRIT or design-specific protocol guideline",
    "real-world evidence": "STROBE plus RECORD or specialty RWE guidance",
    "rwe": "STROBE plus RECORD or specialty RWE guidance",
    "observational": "STROBE",
    "cohort": "STROBE",
    "case-control": "STROBE",
    "cross-sectional": "STROBE",
    "icaml": "ICAML-style clinical AI implementation frame; cross-map to DECIDE-AI/SQUIRE/STROBE/CONSORT-AI/STARD-AI/TRIPOD+AI only when appropriate",
    "ai clinical quality": "ICAML-style clinical AI implementation frame; cross-map to SQUIRE or DECIDE-AI when appropriate",
    "clinical ai": "ICAML-style clinical AI implementation frame; cross-map to DECIDE-AI/SQUIRE/STROBE/CONSORT-AI/STARD-AI/TRIPOD+AI only when appropriate",
    "ai healthcare": "ICAML-style clinical AI implementation frame; cross-map to DECIDE-AI/SQUIRE/STROBE/CONSORT-AI/STARD-AI/TRIPOD+AI only when appropriate",
    "cdss": "ICAML-style clinical AI implementation frame or DECIDE-AI depending on evaluation stage",
    "triage": "ICAML-style clinical AI workflow frame; use STARD-AI only for diagnostic accuracy against a reference standard",
    "diagnostic efficiency": "ICAML-style clinical AI workflow frame; use STARD-AI only for diagnostic accuracy against a reference standard",
    "ai-assisted diagnosis": "ICAML-style clinical AI workflow frame unless the primary endpoint is diagnostic accuracy against a reference standard",
    "workflow": "ICAML-style clinical AI workflow or SQUIRE/STROBE depending on design",
    "diagnostic": "STARD",
    "prognostic": "TRIPOD",
    "prediction model": "TRIPOD or TRIPOD+AI",
    "medical ai": "TRIPOD+AI, STARD-AI, CONSORT-AI, DECIDE-AI, or ICAML depending on task",
    "systematic review": "PRISMA; usually use a study-characteristics table",
    "economic evaluation": "CHEERS",
    "quality improvement": "SQUIRE",
    "qualitative": "SRQR or COREQ",
    "animal": "ARRIVE",
}


DEFAULT_BLOCKS = {
    "demographics": ["Age", "Sex", "Race and ethnicity"],
    "clinical": ["Body mass index", "Disease duration", "Disease severity", "Key comorbidities"],
    "care": ["Prior medication use", "Healthcare utilization", "Site or region"],
    "data": ["Calendar period", "Data source", "Missing key covariates"],
}


def normalize(text):
    return str(text or "").strip().lower()


def infer_guideline(study_type):
    key = normalize(study_type)
    for pattern, guideline in GUIDELINES.items():
        if pattern in key:
            return guideline
    return "Search EQUATOR by study type and clinical area; use the closest design-specific guideline"


def infer_columns(spec):
    groups = spec.get("groups") or []
    include_overall = spec.get("include_overall", True)
    columns = ["Characteristic"]
    if include_overall:
        columns.append(f"Overall (n = {spec.get('overall_n', '')})")
    for group in groups:
        if isinstance(group, dict):
            label = group.get("label", "Group")
            n = group.get("n", "")
        else:
            label = str(group)
            n = ""
        columns.append(f"{label} (n = {n})")
    if spec.get("include_smd"):
        columns.append("SMD")
    if spec.get("include_p_values"):
        columns.append("P value")
    return columns


def infer_variables(spec):
    variables = spec.get("variables")
    if variables:
        rows = []
        for item in variables:
            if isinstance(item, str):
                rows.append({"name": item, "summary": ""})
            else:
                rows.append({
                    "name": item.get("name", "Variable"),
                    "summary": item.get("summary", ""),
                })
        return rows
    rows = []
    for block_vars in DEFAULT_BLOCKS.values():
        for name in block_vars:
            rows.append({"name": name, "summary": ""})
    return rows


def infer_design_warnings(spec):
    study_type = normalize(spec.get("study_type", ""))
    warnings = []
    if any(term in study_type for term in ["rwe", "real-world", "observational", "cohort"]):
        if not spec.get("time_zero"):
            warnings.append("Define time zero/index date before finalizing Table 1 or flowchart denominators.")
        warnings.append("Use DAG/clinical prior knowledge for PS covariates; exclude intermediates, colliders, post-index variables, and outcome/post-outcome variables.")
        warnings.append("Prefer SMDs over baseline p values for balance; SMD <0.1 is a common descriptive target, not proof of no confounding.")
    if any(term in study_type for term in ["clinical ai", "ai healthcare", "ai clinical quality", "cdss", "triage", "workflow", "quality improvement", "diagnostic efficiency", "ai-assisted diagnosis"]):
        warnings.append("Use ICAML-style workflow evaluation when the primary question is implementation, quality, triage, CDSS, or human-AI workflow impact rather than model development.")
        warnings.append("Track AI trigger, output generation, clinician visibility, acceptance/override, downstream action, safety ascertainment, adoption, and fairness strata.")
    if any(term in study_type for term in ["diagnostic", "radiology", "imaging"]):
        warnings.append("Declare one-gate versus two-gate design and audit spectrum, verification, and reference-standard bias.")
        warnings.append("Separate patient-level, lesion-level, image-level, and reader-level denominators when applicable.")
    if any(term in study_type for term in ["prediction", "prognostic", "medical ai", "survival"]):
        warnings.append("Define prediction time zero, outcome horizon, event count, censoring, and data split logic.")
        warnings.append("Plan discrimination, calibration, C-index/time-dependent C-index, and external validation where applicable.")
    if any(term in study_type for term in ["rct", "randomized", "clinical trial"]):
        warnings.append("Use randomized arms and avoid baseline p values unless the SAP or journal explicitly requires them.")
        warnings.append("CONSORT flow must track randomized, allocated, followed-up, discontinued, and analyzed participants by arm.")
    return warnings


def render_flowchart(spec):
    if spec.get("flowchart") is False:
        return ""
    study_type = normalize(spec.get("study_type", ""))
    if any(term in study_type for term in ["rct", "randomized", "clinical trial"]):
        return """```mermaid
flowchart TD
  A["Assessed for eligibility (n=)"] --> B["Excluded (n=): not meeting criteria; declined; other"]
  A --> C["Randomized (n=)"]
  C --> D["Allocated to intervention (n=)"]
  C --> E["Allocated to control (n=)"]
  D --> F["Lost to follow-up/discontinued (n=)"]
  E --> G["Lost to follow-up/discontinued (n=)"]
  F --> H["Analyzed intervention arm (n=)"]
  G --> I["Analyzed control arm (n=)"]
```"""
    if any(term in study_type for term in ["prediction", "prognostic", "medical ai", "survival"]):
        return """```mermaid
flowchart TD
  A["Source population/data repository (n=)"] --> B["Eligible prediction-time observations (n=)"]
  B --> C["Excluded: no outcome window, missing predictors, invalid timing (n=)"]
  C --> D["Modeling dataset at prediction time zero (n=; events=)"]
  D --> E["Development/training cohort (n=; events=)"]
  D --> F["Internal validation cohort (n=; events=)"]
  D --> G["External/temporal/geographic test cohort (n=; events=)"]
```"""
    if any(term in study_type for term in ["clinical ai", "ai healthcare", "ai clinical quality", "cdss", "triage", "workflow", "quality improvement", "diagnostic efficiency", "ai-assisted diagnosis"]):
        return """```mermaid
flowchart TD
  A["Clinical population or encounter stream (n=)"] --> B["Eligible encounters before AI trigger (n=)"]
  B --> C["Workflow entry point: triage/order/result/message/case queue (n=)"]
  C --> D["AI trigger criteria met (n=)"]
  D --> E["AI output generated successfully (n=)"]
  E --> F["AI output shown to clinician/team (n=)"]
  F --> G["Clinician action accepted, modified, overridden, or ignored (n=)"]
  G --> H["Downstream workflow or clinical action completed (n=)"]
  H --> I["Outcome/safety ascertainment complete (n=)"]
  I --> J["Final analyzed encounters/patients/tasks (n=)"]
  E --> K["AI output failure, unavailable data, timeout, or unsafe output (n=)"]
  F --> L["Not reviewed due to workflow, staffing, interface, or alert fatigue (n=)"]
```"""
    if any(term in study_type for term in ["diagnostic", "radiology", "imaging"]):
        return """```mermaid
flowchart TD
  A["Patients/images assessed for eligibility (n=)"] --> B["Excluded before index test (n=)"]
  A --> C["Index test performed/interpretable (n=)"]
  C --> D["Reference standard performed (n=)"]
  D --> E["Disease present (n=)"]
  D --> F["Disease absent (n=)"]
  C --> G["Indeterminate/missing index test (n=)"]
  D --> H["Incomplete/unavailable reference standard (n=)"]
  E --> I["Included in accuracy analysis (n=)"]
  F --> I
```"""
    return """```mermaid
flowchart TD
  A["Source data/population (n=)"] --> B["Potentially eligible participants (n=)"]
  B --> C["Applied eligibility criteria before time zero (n excluded=)"]
  C --> D["Defined time zero/index date (n=)"]
  D --> E["Exposure/treatment groups assigned (n=)"]
  E --> F["Excluded for insufficient lookback or baseline covariates (n=)"]
  F --> G["Follow-up started; outcome ascertainment possible (n=)"]
  G --> H["Matched/weighted/trimmed analytic cohort (n=)"]
  H --> I["Final primary analysis cohort (n=)"]
  H --> J["Sensitivity-analysis cohorts: complete-case, MI, alternative algorithms"]
```"""


def render_matching(spec):
    matching = spec.get("matching")
    if not matching:
        return [
            "- State whether matching/weighting is planned.",
            "- If planned, report algorithm, covariates, caliper/ratio/replacement, common support, discarded records, and post-design balance.",
        ]
    if isinstance(matching, str):
        return [f"- Planned method: {matching}"]
    lines = []
    for key, value in matching.items():
        lines.append(f"- {key}: {value}")
    return lines


def render_missing_and_sensitivity(spec):
    lines = []
    missing = spec.get("missing_data")
    sensitivity = spec.get("sensitivity_analyses")
    if missing:
        if isinstance(missing, str):
            lines.append(f"- Missing-data plan: {missing}")
        else:
            for key, value in missing.items():
                lines.append(f"- Missing-data {key}: {value}")
    else:
        lines.append("- Describe missingness by variable and group; use MI when material missingness makes complete-case analysis fragile.")
    if sensitivity:
        if isinstance(sensitivity, list):
            lines.extend([f"- Sensitivity: {item}" for item in sensitivity])
        else:
            lines.append(f"- Sensitivity: {sensitivity}")
    else:
        lines.append("- Compare MI versus complete-case/non-imputed results when MI is used.")
        lines.append("- Consider alternative matching/weighting, covariate sets, trimming, negative controls, E-values, or model forms when design-sensitive.")
    return lines


def score_study_design(spec):
    study_type = normalize(spec.get("study_type", ""))
    variables = spec.get("variables") or []
    groups = spec.get("groups") or []
    notes = spec.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]

    is_rwe = any(term in study_type for term in ["rwe", "real-world", "observational", "cohort"])
    is_ai_workflow = any(term in study_type for term in [
        "icaml", "clinical ai", "ai healthcare", "ai clinical quality", "cdss",
        "triage", "workflow", "quality improvement", "diagnostic efficiency",
        "ai-assisted diagnosis",
    ])
    is_diagnostic = any(term in study_type for term in ["diagnostic", "radiology", "imaging"])
    is_prediction = any(term in study_type for term in ["prediction", "prognostic", "medical ai", "survival"])
    is_rct = any(term in study_type for term in ["rct", "randomized", "clinical trial"])

    design = 0.8
    if spec.get("study_type"):
        design += 0.3
    if groups or spec.get("comparator"):
        design += 0.3
    if spec.get("time_zero"):
        design += 0.3
    if spec.get("ai_intervention") or spec.get("matching"):
        design += 0.2
    design = min(design, 2.0)

    flow = 0.5
    if spec.get("flowchart") is not False:
        flow += 0.3
    if spec.get("time_zero"):
        flow += 0.3
    if groups:
        flow += 0.2
    if is_ai_workflow and spec.get("workflow_stage"):
        flow += 0.2
    flow = min(flow, 1.5)

    table = 0.4
    if variables:
        table += min(len(variables) / 8, 0.5)
    if spec.get("include_smd"):
        table += 0.2
    if not spec.get("include_p_values"):
        table += 0.2
    if spec.get("overall_n") or groups:
        table += 0.2
    table = min(table, 1.5)

    stats = 0.4
    if spec.get("matching"):
        stats += 0.35
    if spec.get("missing_data"):
        stats += 0.35
    sensitivity = spec.get("sensitivity_analyses")
    if sensitivity:
        stats += 0.5 if isinstance(sensitivity, list) and len(sensitivity) >= 3 else 0.25
    if is_rwe and spec.get("time_zero"):
        stats += 0.2
    if is_ai_workflow and spec.get("comparator"):
        stats += 0.2
    stats = min(stats, 2.0)

    guideline = 0.45
    if infer_guideline(spec.get("study_type")):
        guideline += 0.25
    if notes:
        guideline += 0.15
    if spec.get("benchmark") or spec.get("journal"):
        guideline += 0.15
    guideline = min(guideline, 1.0)

    journal_fit = 0.35
    if spec.get("journal"):
        journal_fit += 0.25
    if not spec.get("include_p_values"):
        journal_fit += 0.15
    if spec.get("include_smd") or is_rct:
        journal_fit += 0.15
    if variables and len(variables) <= 16:
        journal_fit += 0.1
    journal_fit = min(journal_fit, 1.0)

    safety = 0.25
    safety_terms = " ".join([str(item) for item in variables] + notes + [str(sensitivity)])
    for term in ["safety", "fairness", "subgroup", "equity", "adjudication", "harms", "override"]:
        if term in normalize(safety_terms):
            safety += 0.15
    if is_ai_workflow and (spec.get("ai_intervention") and spec.get("workflow_stage")):
        safety += 0.2
    safety = min(safety, 1.0)

    blockers = []
    if (is_rwe or is_ai_workflow or is_prediction) and not spec.get("time_zero"):
        blockers.append("Time zero/index/prediction/workflow anchor is missing.")
    if is_rwe and not spec.get("matching"):
        blockers.append("RWE/observational design lacks an explicit matching, weighting, or confounding-control plan.")
    if is_ai_workflow and not spec.get("ai_intervention"):
        blockers.append("AI healthcare study lacks a clear AI intervention/workflow role.")
    if is_ai_workflow and not spec.get("comparator"):
        blockers.append("AI healthcare study lacks a comparator or deployment contrast.")
    if is_diagnostic and "reference" not in normalize(" ".join([str(v) for v in variables] + notes)):
        blockers.append("Diagnostic design should define reference-standard handling.")
    if is_prediction and "event" not in normalize(" ".join([str(v) for v in variables] + notes)):
        blockers.append("Prediction/survival design should report event counts and validation logic.")
    if is_rct and spec.get("include_p_values"):
        blockers.append("RCT Table 1 includes baseline p values; top journals usually discourage this.")
    if not sensitivity:
        blockers.append("Sensitivity-analysis plan is absent or underspecified.")

    scores = {
        "Research question and design fit": (round(design, 1), 2.0),
        "Enrollment, time anchor, and flowchart": (round(flow, 1), 1.5),
        "Table 1 and baseline/context characterization": (round(table, 1), 1.5),
        "Statistical design and sensitivity analyses": (round(stats, 1), 2.0),
        "Guideline compliance and reproducibility": (round(guideline, 1), 1.0),
        "Top-journal narrative and presentation fit": (round(journal_fit, 1), 1.0),
        "Safety, ethics, equity, and implementation realism": (round(safety, 1), 1.0),
    }
    total = round(sum(value for value, _ in scores.values()), 1)

    cap = 10.0
    for blocker in blockers:
        if "Time zero" in blocker:
            cap = min(cap, 6.0)
        elif "confounding-control" in blocker:
            cap = min(cap, 6.0)
        elif "AI healthcare" in blocker:
            cap = min(cap, 6.5)
        elif "reference-standard" in blocker:
            cap = min(cap, 6.0)
        elif "event counts" in blocker:
            cap = min(cap, 6.5)
        elif "baseline p values" in blocker:
            cap = min(cap, 8.0)
        elif "Sensitivity" in blocker:
            cap = min(cap, 7.0)
    total = min(total, cap)

    if total >= 8.5:
        ceiling = min(10.0, total + 0.8)
    elif total >= 7.0:
        ceiling = min(9.0, total + 1.2)
    else:
        ceiling = min(8.0, total + 1.5)

    strengths = []
    if spec.get("time_zero"):
        strengths.append("Clear time/index/workflow anchor is specified.")
    if spec.get("include_smd") and not spec.get("include_p_values"):
        strengths.append("Balance display favors SMDs and avoids baseline p-value dependence.")
    if sensitivity:
        strengths.append("Sensitivity analyses are prespecified.")
    if is_ai_workflow and spec.get("ai_intervention") and spec.get("workflow_stage"):
        strengths.append("AI workflow role and clinical workflow stage are explicit.")

    priorities = []
    if blockers:
        priorities.extend(blockers[:3])
    if "Sensitivity-analysis plan is absent or underspecified." not in blockers and sensitivity:
        priorities.append("Map each sensitivity analysis to the specific bias it addresses.")
    priorities.append("Ensure the final flowchart denominators reconcile exactly with Table 1 column n.")
    priorities.append("Add a concise top-journal caption and footnote set with denominator, missingness, and analysis-set definitions.")

    return scores, round(total, 1), round(ceiling, 1), blockers, strengths, priorities


def render_scoring_report(spec):
    scores, total, ceiling, blockers, strengths, priorities = score_study_design(spec)
    benchmark = spec.get("benchmark") or "JCR Top-1 Medicine benchmark"
    target_category = spec.get("target_jcr_category") or "Medicine, General & Internal unless a specialty category is specified"
    lines = [
        "## JCR Top-1 Benchmark Scoring Report",
        "",
        f"Benchmark used: {benchmark}",
        f"Target JCR category: {target_category}",
        f"Overall score: {total:.1f} / 10",
        f"Post-revision ceiling: {ceiling:.1f} / 10",
        "",
        "| Domain | Score | Rationale |",
        "| --- | ---: | --- |",
    ]
    for domain, (score, max_score) in scores.items():
        lines.append(f"| {domain} | {score:.1f}/{max_score:.1f} | Heuristic first-pass score; refine manually against `references/benchmark-scoring.md`. |")
    lines.extend(["", "Critical blockers:"])
    if blockers:
        lines.extend([f"- {item}" for item in blockers])
    else:
        lines.append("- No automatic critical blocker detected; perform manual benchmark review.")
    lines.extend(["", "Top strengths:"])
    if strengths:
        lines.extend([f"- {item}" for item in strengths])
    else:
        lines.append("- Strengths require manual assessment after complete protocol details are supplied.")
    lines.extend(["", "Revision priorities:"])
    lines.extend([f"{idx}. {item}" for idx, item in enumerate(priorities[:5], start=1)])
    lines.append("")
    return "\n".join(lines)


def markdown_table(columns, rows):
    header = "| " + " | ".join(columns) + " |"
    align = "| " + " | ".join(["---"] + ["---:"] * (len(columns) - 1)) + " |"
    body = []
    for row in rows:
        label = row["name"]
        if row.get("summary"):
            label = f"{label}, {row['summary']}"
        body.append("| " + " | ".join([label] + [""] * (len(columns) - 1)) + " |")
    return "\n".join([header, align] + body)


def render(spec):
    study_type = spec.get("study_type", "unspecified study")
    guideline = infer_guideline(study_type)
    journal = spec.get("journal", "unspecified journal")
    population = spec.get("population", "study population")
    columns = infer_columns(spec)
    rows = infer_variables(spec)
    notes = spec.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]

    lines = [
        "# Study Design Memo",
        "",
        f"- Study type: {study_type}",
        f"- Guideline alignment: {guideline}",
        f"- Target journal/style: {journal}",
        f"- Population: {population}",
        f"- Include overall column: {bool(spec.get('include_overall', True))}",
        f"- Include SMD: {bool(spec.get('include_smd', False))}",
        f"- Include p values: {bool(spec.get('include_p_values', False))}",
        f"- Time zero/index anchor: {spec.get('time_zero', 'not specified')}",
        f"- AI intervention/workflow role: {spec.get('ai_intervention', 'not specified')}",
        f"- Workflow stage: {spec.get('workflow_stage', 'not specified')}",
        f"- Comparator: {spec.get('comparator', 'not specified')}",
        "",
        "## Column Logic",
        "",
        ", ".join(columns),
        "",
        "## Table Skeleton",
        "",
        markdown_table(columns, rows),
        "",
        "## Flowchart Skeleton",
        "",
        render_flowchart(spec),
        "",
        "## Matching Or Grouping Plan",
        "",
        *render_matching(spec),
        "",
        "## Missing Data And Sensitivity Analyses",
        "",
        *render_missing_and_sensitivity(spec),
        "",
        "## Footnote Starter",
        "",
        "Data are shown as mean (SD), median (IQR), or No. (%) unless otherwise indicated. "
        "Percentages should be calculated using the prespecified denominator rule. "
        "Define missingness, weighting, matching, tests, SMDs, and abbreviations here.",
        "",
        render_scoring_report(spec),
    ]
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend([f"- {note}" for note in notes])
    warnings = infer_design_warnings(spec)
    if warnings:
        lines.extend(["", "## Design Warnings", ""])
        lines.extend([f"- {warning}" for warning in warnings])
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to JSON study specification")
    parser.add_argument("--out", help="Output Markdown path")
    parser.add_argument("--out-dir", help="Output directory for a multi-format package")
    parser.add_argument(
        "--formats",
        default="xlsx,csv,html,md",
        help="Comma-separated package formats: xlsx,csv,html,md",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if args.out_dir:
        from generate_study_package import generate_package

        formats = {item.strip().casefold() for item in args.formats.split(",") if item.strip()}
        supported = {"xlsx", "csv", "html", "md", "markdown"}
        invalid = formats - supported
        if invalid:
            raise ValueError(f"Unsupported formats: {', '.join(sorted(invalid))}")
        outputs = generate_package(spec, spec_path.parent, Path(args.out_dir), formats)
        for output in outputs:
            print(output)
        return
    output = render(spec)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
