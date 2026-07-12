#!/usr/bin/env python3
"""Generate a study design memo or a multi-format study design package.

Input: JSON study specification.
Output: Markdown, or CSV/XLSX/HTML/Markdown when --out-dir is supplied.
"""

import argparse
import json
from pathlib import Path

from sample_size import estimate_sample_size, markdown_sample_size


GUIDELINES = {
    "controlled interrupted time series": "SQUIRE 2.0 plus TREND; RECORD for routine data; DECIDE-AI for early live AI evaluation",
    "interrupted time series": "SQUIRE 2.0 plus TREND; RECORD for routine data; DECIDE-AI for early live AI evaluation",
    "difference-in-differences": "TREND plus STROBE; RECORD for routine data; SQUIRE 2.0 for quality improvement",
    "stepped-wedge": "CONSORT extension for stepped-wedge cluster randomized trials; CONSORT-AI when applicable",
    "rct": "CONSORT 2025 or applicable CONSORT extension",
    "randomized controlled trial": "CONSORT 2025 or applicable CONSORT extension",
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
    "meta-analysis": "PRISMA; use the design-specific risk-of-bias tool",
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
                label = item.get("label", item.get("name", "Variable"))
                if item.get("unit"):
                    label = f"{label}, {item['unit']}"
                rows.append({
                    "name": label,
                    "summary": item.get("display_suffix", ""),
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
    is_causal_observational = any(term in study_type for term in ["causal", "comparative effectiveness", "target trial", "rwe", "real-world evidence"])
    is_its = any(term in study_type for term in ["interrupted time series", "difference-in-differences", "difference in differences"])
    if is_causal_observational:
        if not spec.get("time_zero"):
            warnings.append("Define time zero/index date before finalizing Table 1 or flowchart denominators.")
        warnings.append("Use DAG/clinical prior knowledge for PS covariates; exclude intermediates, colliders, post-index variables, and outcome/post-outcome variables.")
        warnings.append("Prefer SMDs over baseline p values for balance; SMD <0.1 is a common descriptive target, not proof of no confounding.")
    elif any(term in study_type for term in ["observational", "cohort", "cross-sectional", "case-control"]):
        warnings.append("Do not add propensity-score methods unless the study has a defined causal contrast and a defensible time zero.")
    if is_its:
        warnings.append("Estimate intervention-related level and slope changes with repeated observations; one pre and one post aggregate do not constitute an ITS.")
        warnings.append("Address autocorrelation, seasonality, co-interventions, intervention timing, ramp-up, and composition changes; use a concurrent control series when available.")
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
    if "controlled interrupted time series" in study_type or "cits" in study_type:
        return """```mermaid
flowchart TD
  A["Intervention and concurrent control source streams"] --> B["Common eligibility and stable outcome definition"]
  B --> C["Repeated pre-intervention observations by series"]
  C --> D["Prespecified deployment date and ramp-up period"]
  D --> E["Repeated post-intervention observations by series"]
  E --> F["Complete time points with case-mix and exposure denominators"]
  F --> G["Controlled segmented-regression analysis"]
```"""
    if "interrupted time series" in study_type or "difference-in-differences" in study_type or "difference in differences" in study_type:
        return """```mermaid
flowchart TD
  A["Clinical/site stream and sampling frame"] --> B["Stable eligibility and outcome definition"]
  B --> C["Repeated pre-intervention observations"]
  C --> D["Deployment/rollout and prespecified transition period"]
  D --> E["Repeated post-intervention observations"]
  E --> F["Time points retained/excluded with reasons"]
  F --> G["Segmented regression or panel/event-study analysis"]
```"""
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
    if any(term in study_type for term in ["systematic review", "meta-analysis"]):
        return """```mermaid
flowchart TD
  A["Records identified from databases/registers"] --> B["Duplicates removed"]
  B --> C["Titles/abstracts screened"]
  C --> D["Full texts assessed"]
  D --> E["Excluded with reasons"]
  D --> F["Studies included in qualitative synthesis"]
  F --> G["Studies included in each meta-analysis"]
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
    study_type = normalize(spec.get("study_type", ""))
    if any(term in study_type for term in ["prediction", "prognostic"]):
        return [
            "- Propensity-score matching is not a default prediction-model bias correction.",
            "- Use bootstrap/repeated resampling for optimism, shrinkage or penalization, calibration, discrimination, clinical utility, and temporal/geographic/site external validation.",
        ]
    if any(term in study_type for term in ["diagnostic", "radiology", "imaging"]):
        return [
            "- Do not use PSM as a substitute for representative one-gate sampling or verification-bias control.",
            "- Prefer consecutive/random enrollment, blinded index/reference interpretation, complete verification, prespecified thresholds, and paired/randomized comparison for multiple tests.",
        ]
    if any(term in study_type for term in ["interrupted time series", "difference-in-differences", "difference in differences"]):
        return [
            "- PSM is not the primary design control. Preserve repeated time points and intervention timing.",
            "- Use segmented regression or panel/event-study models with autocorrelation/seasonality, baseline trends, concurrent controls, cluster inference, and co-intervention checks as applicable.",
        ]
    if any(term in study_type for term in ["rct", "randomized", "stepped-wedge"]):
        return ["- Use randomized allocation, concealment, prespecified estimand, intention-to-treat analysis, and cluster/period effects when applicable; do not replace randomization with PSM."]
    if any(term in study_type for term in ["systematic review", "meta-analysis"]):
        return ["- Not applicable as a participant-grouping method. Use design-specific risk-of-bias tools and a prespecified evidence-synthesis model."]
    matching = spec.get("matching")
    if not matching:
        return [
            "- State the causal estimand before deciding whether matching/weighting is needed.",
            "- If no causal group contrast is intended, explain the design-specific bias controls instead of adding propensity-score methods.",
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
    study_type = normalize(spec.get("study_type", ""))
    if missing:
        if isinstance(missing, str):
            lines.append(f"- Missing-data plan: {missing}")
        else:
            for key, value in missing.items():
                lines.append(f"- Missing-data {key}: {value}")
    else:
        lines.append("- Describe missingness and use a design-appropriate strategy; multiple imputation is not automatically required for every design.")
    if sensitivity:
        if isinstance(sensitivity, list):
            lines.extend([f"- Sensitivity: {item}" for item in sensitivity])
        else:
            lines.append(f"- Sensitivity: {sensitivity}")
    else:
        if any(term in study_type for term in ["prediction", "prognostic"]):
            lines.extend([
                "- Internal validation: bootstrap or repeated resampling; quantify optimism and calibration.",
                "- External validation: temporal, geographic, or site-based data; report discrimination, calibration, and clinical utility.",
            ])
        elif any(term in study_type for term in ["interrupted time series", "difference-in-differences", "difference in differences"]):
            lines.extend([
                "- Check alternative intervention dates, ramp-up exclusion, autocorrelation/seasonality structures, pre-trends, co-interventions, and unaffected outcomes/series.",
                "- Compare controlled and uncontrolled estimates when a concurrent control is available.",
            ])
        elif any(term in study_type for term in ["diagnostic", "radiology", "imaging"]):
            lines.extend([
                "- Assess indeterminate results, missing reference standards, threshold choice, reader/order effects, and device/site variation.",
                "- For comparative accuracy, preserve paired data and apply QUADAS-C alongside QUADAS-3 in appraisal contexts.",
            ])
        elif any(term in study_type for term in ["rct", "randomized", "stepped-wedge"]):
            lines.extend(["- Address missing outcomes, protocol deviations, estimand strategy, clustering/period effects, and harms; do not require observational unmeasured-confounding metrics by reflex."])
        elif any(term in study_type for term in ["systematic review", "meta-analysis"]):
            lines.extend(["- Assess design-specific risk of bias, heterogeneity, influential studies, small-study effects when interpretable, and certainty of evidence."])
        else:
            lines.extend([
                "- Compare MI versus complete-case/non-imputed results only when MI is used and the assumptions are relevant.",
                "- Select robustness analyses that target the actual design threats rather than a fixed checklist.",
            ])
    return lines


def score_study_design(spec):
    study_type = normalize(spec.get("study_type", ""))
    variables = spec.get("variables") or []
    groups = spec.get("groups") or []
    notes = spec.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]

    is_rwe = any(term in study_type for term in ["rwe", "real-world evidence", "comparative effectiveness", "target trial", "observational causal"])
    is_its = any(term in study_type for term in ["interrupted time series", "difference-in-differences", "difference in differences"])
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
    if spec.get("confirmed_design"):
        design += 0.2
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
    if spec.get("flow_guidance"):
        flow += 0.1
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
    if spec.get("table1_guidance"):
        table += 0.3
    if any(term in study_type for term in ["systematic review", "meta-analysis", "scoping review"]):
        table = max(table, 1.0)
    table = min(table, 1.5)

    stats = 0.4
    if is_rwe and spec.get("matching"):
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
    if is_its and spec.get("time_points"):
        stats += 0.35
    if is_prediction and (spec.get("validation") or spec.get("external_validation")):
        stats += 0.5
    if is_diagnostic and spec.get("reference_standard"):
        stats += 0.35
    if spec.get("analysis_methods"):
        stats += 0.5
    if spec.get("bias_tools"):
        stats += 0.2
    sample_size_result = estimate_sample_size(spec)
    if sample_size_result["status"] == "estimated":
        stats += 0.2
    else:
        stats -= 0.3
    stats = min(stats, 2.0)

    guideline = 0.45
    if infer_guideline(spec.get("study_type")):
        guideline += 0.25
    if notes:
        guideline += 0.15
    if spec.get("benchmark") or spec.get("journal"):
        guideline += 0.15
    if spec.get("guideline_stack"):
        guideline += 0.2
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
    if (is_rwe or is_its or is_diagnostic) and not sensitivity:
        blockers.append("Design-specific robustness or sensitivity plan is absent or underspecified.")
    if is_prediction and not (spec.get("validation") or spec.get("external_validation")):
        blockers.append("Prediction design lacks a clear internal/external validation strategy.")
    if sample_size_result["status"] != "estimated":
        blockers.append("Sample size is not estimable because design-specific assumptions are missing or unsupported.")

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
        elif "robustness" in blocker:
            cap = min(cap, 7.0)
        elif "validation strategy" in blocker:
            cap = min(cap, 6.5)
        elif "Sample size" in blocker:
            cap = min(cap, 7.5)
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
    if sample_size_result["status"] == "estimated":
        strengths.append("Sample size assumptions, analyzable sample, and inflated recruitment target are explicit.")
    if is_ai_workflow and spec.get("ai_intervention") and spec.get("workflow_stage"):
        strengths.append("AI workflow role and clinical workflow stage are explicit.")

    priorities = []
    if blockers:
        priorities.extend(blockers[:3])
    if sensitivity:
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


def render_footnote(spec):
    study_type = normalize(spec.get("study_type", ""))
    base = "Data are shown as mean (SD), median (IQR), or No. (%) unless otherwise indicated. Define denominator and missingness rules."
    if any(term in study_type for term in ["prediction", "prognostic"]):
        return base + " Define prediction time zero, outcome events/horizon, predictor timing, imputation, clustering, dataset partitions, internal validation, and external validation."
    if any(term in study_type for term in ["diagnostic", "radiology", "imaging"]):
        return base + " Define patient/image/lesion units, sampling pathway, index tests, reference standard, blinding, paired completeness, indeterminate results, thresholds, and reader/device structure."
    if any(term in study_type for term in ["interrupted time series", "difference-in-differences", "difference in differences"]):
        return base + " Define series/cluster, observation frequency, repeated pre/post periods, intervention point, ramp-up, outcome denominator/offset, baseline trend, seasonality, autocorrelation, and concurrent control."
    if any(term in study_type for term in ["rct", "randomized", "stepped-wedge"]):
        return base + " Define randomized analysis set, cluster/sequence when applicable, stratification factors, protocol deviations, estimand, and harms population. Baseline significance tests are not used to validate randomization."
    if any(term in study_type for term in ["systematic review", "meta-analysis"]):
        return "Each row represents one included study or analysis. Define design, population, intervention/exposure/test/model, comparator, outcome, follow-up, effect measure, and design-specific risk-of-bias judgement."
    if any(term in study_type for term in ["rwe", "real-world evidence", "comparative effectiveness", "target trial", "observational causal"]):
        return base + " Define time zero, covariate lookback, weighting/matching, SMD, missing-data handling, and analysis-set rules."
    return base + " Define sampling, measurement timing, clustering or survey weights, and any inferential comparisons."


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
        f"- Confirmed design ID: {spec.get('confirmed_design', 'not triaged')}",
        f"- Reporting guideline stack: {'; '.join(spec.get('guideline_stack', [])) or guideline}",
        "",
        "## Design-Specific Method Stack",
        "",
        "Reporting guidelines:",
        *[f"- {item}" for item in (spec.get("guideline_stack") or [guideline])],
        "",
        "Risk-of-bias/appraisal tools:",
        *[f"- {item}" for item in (spec.get("bias_tools") or ["Select after confirming the design and estimand."])],
        "",
        "Analysis/validation methods:",
        *[f"- {item}" for item in (spec.get("analysis_methods") or ["Select methods that address the confirmed design threats."])],
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
        markdown_sample_size(estimate_sample_size(spec)),
        "",
        "## Design-Specific Bias Control And Grouping Plan",
        "",
        *render_matching(spec),
        "",
        "## Missing Data And Sensitivity Analyses",
        "",
        *render_missing_and_sensitivity(spec),
        "",
        "## Footnote Starter",
        "",
        render_footnote(spec),
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
    parser.add_argument("--triage", action="store_true", help="Run proposal triage and one-question clarification")
    parser.add_argument(
        "--formats",
        default="xlsx,csv,html,md",
        help="Comma-separated package formats: xlsx,csv,html,md",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if args.triage or spec.get("proposal"):
        from classify_study import DESIGNS, render_markdown as render_triage, triage

        triage_result = triage(spec)
        if triage_result["ready_for_design"]:
            profile = triage_result["recommended_design"]
            spec.setdefault("study_type", DESIGNS[spec["confirmed_design"]]["label"])
            spec.setdefault("guideline_stack", list(dict.fromkeys(profile["reporting"] + triage_result["guideline_overlays"])))
            spec.setdefault("bias_tools", profile["bias_tools"])
            spec.setdefault("analysis_methods", profile["methods"])
            spec.setdefault("table1_guidance", profile["table"])
            spec.setdefault("flow_guidance", profile["flow"])
        else:
            triage_markdown = render_triage(triage_result)
            triage_json = json.dumps(triage_result, ensure_ascii=False, indent=2)
            if args.out_dir:
                output_dir = Path(args.out_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "study-intake.md").write_text(triage_markdown, encoding="utf-8")
                (output_dir / "study-intake.json").write_text(triage_json, encoding="utf-8")
                print(output_dir / "study-intake.md")
                print(output_dir / "study-intake.json")
            elif args.out:
                Path(args.out).write_text(triage_markdown, encoding="utf-8")
            else:
                print(triage_markdown)
            return
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
