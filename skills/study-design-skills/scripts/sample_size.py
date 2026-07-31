#!/usr/bin/env python3
"""Transparent first-pass sample-size estimators for confirmed study designs."""

import math
from statistics import NormalDist


def _z(probability):
    return NormalDist().inv_cdf(probability)


def _inflate(n, loss_fraction):
    if not 0 <= loss_fraction < 1:
        raise ValueError("loss_fraction must be at least 0 and below 1")
    return math.ceil(n / (1 - loss_fraction))


def _result(method, assumptions, analyzable, recruited, unit, formula, caveats=None, recruited_unit=None):
    return {
        "status": "estimated",
        "method": method,
        "assumptions": assumptions,
        "analyzable_n": int(math.ceil(analyzable)),
        "recruited_n": int(math.ceil(recruited)),
        "unit": unit,
        "recruited_unit": recruited_unit or unit,
        "formula": formula,
        "caveats": caveats or [],
    }


def parallel_proportions(cfg):
    p0 = float(cfg["control_event_rate"])
    p1 = float(cfg["intervention_event_rate"])
    alpha = float(cfg.get("alpha", 0.05))
    power = float(cfg.get("power", 0.80))
    ratio = float(cfg.get("allocation_ratio", 1.0))
    loss = float(cfg.get("loss_fraction", 0.0))
    if not 0 < p0 < 1 or not 0 < p1 < 1 or p0 == p1 or ratio <= 0:
        raise ValueError("event rates must be distinct values in (0,1), and allocation_ratio must be positive")
    za = _z(1 - alpha / 2)
    zb = _z(power)
    # Normal approximation allowing n_intervention / n_control = ratio.
    n_control = ((za + zb) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1) / ratio)) / ((p1 - p0) ** 2)
    n_intervention = ratio * n_control
    analyzable = math.ceil(n_control) + math.ceil(n_intervention)
    recruited = _inflate(analyzable, loss)
    return _result(
        "Two independent proportions, two-sided normal approximation",
        {"control_event_rate": p0, "intervention_event_rate": p1, "absolute_difference": p1 - p0, "alpha": alpha, "power": power, "allocation_ratio": ratio, "loss_fraction": loss, "assumption_source": cfg.get("assumption_source", "Not supplied")},
        analyzable,
        recruited,
        "participants total",
        "n0=[(z1-alpha/2+zpower)^2{p0(1-p0)+p1(1-p1)/r}]/(p1-p0)^2; n1=r*n0",
        ["Confirm with the final primary analysis model, stratification factors, multiplicity plan, and any noninferiority margin."],
    )


def paired_binary(cfg):
    p01 = float(cfg["discordant_control_only"])
    p10 = float(cfg["discordant_intervention_only"])
    alpha = float(cfg.get("alpha", 0.05))
    power = float(cfg.get("power", 0.80))
    loss = float(cfg.get("incomplete_pair_fraction", cfg.get("loss_fraction", 0.0)))
    if p01 < 0 or p10 < 0 or p01 + p10 >= 1 or p01 == p10:
        raise ValueError("directional discordances must be nonnegative, sum below 1, and differ under the alternative")
    za = _z(1 - alpha / 2)
    zb = _z(power)
    discordance = p01 + p10
    difference = abs(p10 - p01)
    analyzable = ((za * math.sqrt(discordance) + zb * math.sqrt(discordance - difference**2)) ** 2) / difference**2
    recruited = _inflate(math.ceil(analyzable), loss)
    return _result(
        "McNemar paired binary comparison using directional discordances",
        {"p01": p01, "p10": p10, "net_paired_difference": p10 - p01, "total_discordance": discordance, "alpha": alpha, "power": power, "incomplete_pair_fraction": loss, "assumption_source": cfg.get("assumption_source", "Not supplied")},
        analyzable,
        recruited,
        "complete participant pairs",
        "n=[z1-alpha/2*sqrt(p01+p10)+zpower*sqrt(p01+p10-(p10-p01)^2)]^2/(p10-p01)^2",
        ["Directional discordances must come from pilot data or defensible literature; symmetric discordance implies no superiority effect.", "Use simulation or exact methods when discordant counts are expected to be sparse."],
        recruited_unit="participants to enroll",
    )


def diagnostic_precision(cfg):
    sensitivity = float(cfg["sensitivity"])
    specificity = float(cfg["specificity"])
    prevalence = float(cfg["prevalence"])
    sens_half_width = float(cfg["sensitivity_half_width"])
    spec_half_width = float(cfg["specificity_half_width"])
    alpha = float(cfg.get("alpha", 0.05))
    loss = float(cfg.get("uninterpretable_or_unverified_fraction", cfg.get("loss_fraction", 0.0)))
    if not all(0 < value < 1 for value in [sensitivity, specificity, prevalence, sens_half_width, spec_half_width]):
        raise ValueError("diagnostic assumptions must be values in (0,1)")
    z = _z(1 - alpha / 2)
    diseased = math.ceil(z**2 * sensitivity * (1 - sensitivity) / sens_half_width**2)
    non_diseased = math.ceil(z**2 * specificity * (1 - specificity) / spec_half_width**2)
    total_for_sensitivity = math.ceil(diseased / prevalence)
    total_for_specificity = math.ceil(non_diseased / (1 - prevalence))
    analyzable = max(total_for_sensitivity, total_for_specificity)
    recruited = _inflate(analyzable, loss)
    return _result(
        "Diagnostic sensitivity/specificity precision",
        {"sensitivity": sensitivity, "specificity": specificity, "prevalence": prevalence, "sensitivity_half_width": sens_half_width, "specificity_half_width": spec_half_width, "alpha": alpha, "uninterpretable_or_unverified_fraction": loss, "required_diseased": diseased, "required_non_diseased": non_diseased, "assumption_source": cfg.get("assumption_source", "Not supplied")},
        analyzable,
        recruited,
        "participants",
        "n_diseased=z^2*Se(1-Se)/dSe^2; n_non-diseased=z^2*Sp(1-Sp)/dSp^2; total=max(n_diseased/Prev,n_non-diseased/(1-Prev))",
        ["For paired comparative accuracy, power the paired difference directly when directional paired results are available; this precision calculation is a supporting floor.", "Account for lesion clustering, readers, centres, and verification strategy separately."],
    )


def survival_events(cfg):
    hazard_ratio = float(cfg["hazard_ratio"])
    alpha = float(cfg.get("alpha", 0.05))
    power = float(cfg.get("power", 0.80))
    allocation = float(cfg.get("intervention_fraction", 0.5))
    event_fraction = float(cfg["event_fraction"])
    loss = float(cfg.get("loss_fraction", 0.0))
    if hazard_ratio <= 0 or hazard_ratio == 1 or not 0 < allocation < 1 or not 0 < event_fraction <= 1:
        raise ValueError("hazard ratio, allocation, and event fraction are invalid")
    events = ((_z(1 - alpha / 2) + _z(power)) ** 2) / (allocation * (1 - allocation) * math.log(hazard_ratio) ** 2)
    analyzable = math.ceil(events / event_fraction)
    recruited = _inflate(analyzable, loss)
    return _result(
        "Schoenfeld proportional-hazards event method",
        {"hazard_ratio": hazard_ratio, "alpha": alpha, "power": power, "intervention_fraction": allocation, "event_fraction": event_fraction, "loss_fraction": loss, "required_events": math.ceil(events), "assumption_source": cfg.get("assumption_source", "Not supplied")},
        analyzable,
        recruited,
        "participants",
        "D=(z1-alpha/2+zpower)^2/[q(1-q){log(HR)}^2]; N=D/event_fraction",
        ["Validate accrual, follow-up, competing risks, nonproportional hazards, and loss assumptions with design-specific software or simulation."],
    )


METHODS = {
    "parallel_proportions": parallel_proportions,
    "paired_binary": paired_binary,
    "diagnostic_precision": diagnostic_precision,
    "survival_events": survival_events,
}


def estimate_sample_size(spec):
    cfg = spec.get("sample_size") or {}
    method = cfg.get("method")
    if not method:
        return {
            "status": "assumptions_required",
            "method": "Not calculated",
            "missing": ["sample_size.method", "design-specific effect or precision assumptions", "alpha", "power or confidence-width target", "loss/incomplete-pair allowance"],
            "caveats": ["Do not infer an effect size from the observed study data after enrollment. Use external evidence, pilot data, or a clinically meaningful target."],
        }
    if method in {"did_event_study_simulation", "its_simulation"}:
        return {
            "status": "assumptions_required",
            "method": method,
            "missing": [
                "number of departments/clusters and rollout waves",
                "pre- and post-rollout time points per cluster",
                "baseline event rate with encounter or patient-time denominator",
                "clinically meaningful level/rate-ratio and dynamic effect trajectory",
                "between-cluster heterogeneity and within-cluster serial correlation",
                "count distribution/overdispersion and seasonal structure",
                "partial-control overlap and anticipated missing periods",
                "alpha, power, attrition and multiplicity choices",
            ],
            "caveats": ["Use simulation under the planned fixed-effects/event-study or segmented count model. Report power across plausible pre-trend, overdispersion, and partial-control scenarios."],
        }
    if method == "cluster_crossover_simulation":
        return {
            "status": "assumptions_required",
            "method": method,
            "missing": [
                "number of nursing technologists/clusters",
                "AB/BA periods and encounters per technologist-period",
                "baseline primary-outcome rate and clinically meaningful improvement",
                "within-technologist and within-period intracluster correlations",
                "between-technologist heterogeneity and period effect",
                "anticipated carryover/learning and transition-window handling",
                "device downtime, missing outcome and protocol-deviation rates",
                "alpha, power, multiplicity and analysis-model specification",
            ],
            "caveats": ["Use simulation under the planned mixed-effects crossover model. Vary cluster size, ICC, period effect, carryover and patient case-mix imbalance."],
        }
    if method not in METHODS:
        return {"status": "unsupported", "method": method, "missing": ["A supported method or an externally validated calculation"], "caveats": ["Use dedicated software or simulation and store its assumptions/results in the specification."]}
    try:
        return METHODS[method](cfg)
    except (KeyError, TypeError, ValueError) as error:
        return {"status": "assumptions_required", "method": method, "missing": [str(error)], "caveats": ["Complete and clinically justify every required assumption before treating the estimate as final."]}


def markdown_sample_size(result):
    lines = ["## Sample Size Estimation", ""]
    if result["status"] != "estimated":
        lines.extend([f"- Status: {result['status']}", f"- Method: {result['method']}", "- Required inputs:"])
        lines.extend(f"  - {item}" for item in result.get("missing", []))
    else:
        lines.extend([
            f"- Method: {result['method']}",
            f"- Analyzable sample: {result['analyzable_n']} {result['unit']}",
            f"- Recruitment target after inflation: {result['recruited_n']} {result['recruited_unit']}",
            f"- Formula: `{result['formula']}`",
            "- Assumptions:",
        ])
        lines.extend(f"  - {key}: {value}" for key, value in result["assumptions"].items())
    if result.get("caveats"):
        lines.append("- Caveats:")
        lines.extend(f"  - {item}" for item in result["caveats"])
    return "\n".join(lines)
