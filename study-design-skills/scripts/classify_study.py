#!/usr/bin/env python3
"""Explainable study-design triage with one-question-at-a-time clarification."""

import argparse
import json
import re
from pathlib import Path


DESIGNS = {
    "controlled_interrupted_time_series": {
        "label": "Controlled interrupted time series (CITS)",
        "reporting": ["SQUIRE 2.0", "TREND", "RECORD when routine data are used", "DECIDE-AI for early live AI evaluation"],
        "bias_tools": ["ROBINS-I for the non-randomized intervention effect", "Cochrane EPOC ITS design criteria"],
        "methods": ["segmented regression for level and slope change", "concurrent control series and intervention-by-time terms", "autocorrelation and seasonality", "ramp-up and co-intervention checks", "negative-control outcome or unaffected series when defensible"],
        "table": "Describe pre-intervention patient/encounter mix and context by intervention/control series; add baseline level, baseline slope, volume, site, staffing, and outcome ascertainment. SMD/PSM is not the default.",
        "flow": "Source streams -> eligibility -> pre-period -> deployment/ramp-up -> post-period, in parallel for intervention and control series -> outcome ascertainment -> analyzed time points.",
    },
    "interrupted_time_series": {
        "label": "Interrupted time series (ITS)",
        "reporting": ["SQUIRE 2.0", "TREND", "RECORD when routine data are used", "DECIDE-AI for early live AI evaluation"],
        "bias_tools": ["ROBINS-I", "Cochrane EPOC ITS design criteria"],
        "methods": ["segmented regression", "level and slope change", "autocorrelation and seasonality", "prespecified intervention point", "co-intervention and falsification checks"],
        "table": "Describe the clinical population and workflow context in pre/post periods plus baseline outcome level, trend, volume, staffing, season, and case mix. Do not present a simple two-column pre/post Table 1 as sufficient control for secular trends.",
        "flow": "Source stream -> eligibility -> repeated pre-intervention observations -> deployment/ramp-up -> repeated post-intervention observations -> analyzed time points.",
    },
    "difference_in_differences": {
        "label": "Difference-in-differences (DiD) / comparative panel design",
        "reporting": ["TREND", "STROBE", "RECORD when routine data are used", "SQUIRE 2.0 for improvement work"],
        "bias_tools": ["ROBINS-I"],
        "methods": ["parallel-trends assessment", "group-by-post interaction", "cluster-robust or multilevel inference", "event-study leads/lags", "spillover and compositional-change checks"],
        "table": "Describe intervention and control groups before treatment, baseline outcome trends, cluster/context variables, and composition over time. Balance weights may be secondary, not automatic.",
        "flow": "Intervention/control clusters -> common eligibility -> pre-period observations -> rollout -> post-period observations -> balanced panel/analytic sample.",
    },
    "stepped_wedge_cluster_rct": {
        "label": "Stepped-wedge cluster randomized trial",
        "reporting": ["CONSORT extension for stepped-wedge cluster randomized trials", "CONSORT-AI when applicable", "SQUIRE 2.0 as an implementation overlay"],
        "bias_tools": ["RoB 2 cluster-randomized domains"],
        "methods": ["randomized rollout sequence", "period and cluster effects", "within-cluster correlation", "intention-to-treat by assigned rollout", "contamination and transition-period handling"],
        "table": "Describe clusters and participants by randomized sequence or intervention status at baseline; include cluster size, setting, baseline outcome, stratification factors, and case mix. Avoid baseline significance tests.",
        "flow": "Clusters assessed -> randomized to sequences -> periods before/after crossover -> participants/encounters analyzed by assigned sequence.",
    },
    "randomized_controlled_trial": {
        "label": "Randomized controlled trial",
        "reporting": ["CONSORT 2025", "CONSORT-AI when an AI intervention is randomized", "SPIRIT/SPIRIT-AI for protocols"],
        "bias_tools": ["RoB 2"],
        "methods": ["allocation concealment", "blinding where feasible", "intention-to-treat", "estimand and missing-outcome strategy", "harms analysis"],
        "table": "Describe randomized arms at baseline with prognostic and stratification variables. Usually omit P values and do not use PSM.",
        "flow": "Eligibility -> randomization -> allocation -> follow-up -> discontinuation -> analysis by arm.",
    },
    "observational_causal": {
        "label": "Observational causal / comparative-effectiveness study",
        "reporting": ["STROBE", "RECORD for routine data", "TARGET for target-trial emulation when applicable"],
        "bias_tools": ["ROBINS-I for non-randomized interventions", "ROBINS-E for exposure effects in evidence synthesis"],
        "methods": ["explicit time zero", "DAG-based confounder selection", "matching/weighting/g-formula as justified", "positivity and balance diagnostics", "missing-data and unmeasured-confounding analyses"],
        "table": "Describe exposure groups at time zero, confounders, disease severity, utilization, missingness, and pre/post-design balance. SMD and PS methods are appropriate only when estimating a causal contrast.",
        "flow": "Source population -> eligibility -> time zero -> exposure assignment -> design/weighting -> follow-up -> outcome -> analytic cohort.",
    },
    "descriptive_observational": {
        "label": "Descriptive or associational observational study",
        "reporting": ["STROBE", "RECORD for routine data"],
        "bias_tools": ["design-specific selection, measurement, and confounding appraisal"],
        "methods": ["sampling-frame definition", "confounder-adjusted association model when needed", "missingness assessment", "cluster/survey weighting when applicable"],
        "table": "Describe the sampled population and scientifically relevant strata. Do not add PSM merely because groups exist.",
        "flow": "Sampling frame -> eligibility -> included participants -> measurements -> complete analytic sample.",
    },
    "diagnostic_accuracy": {
        "label": "Diagnostic accuracy study",
        "reporting": ["STARD 2015", "STARD-AI for AI index tests"],
        "bias_tools": ["QUADAS-3 to inform risk-of-bias domains and primary-study design"],
        "methods": ["one-gate consecutive or random sampling", "prespecified threshold", "blinded index/reference interpretation", "verification of all or a random sample", "sensitivity/specificity with confidence intervals"],
        "table": "Describe the clinical spectrum by reference-standard status, setting, severity, alternative diagnoses, index-test timing, and patient/image/lesion denominators. PSM is not a diagnostic-bias correction.",
        "flow": "Eligibility -> index test -> reference standard -> indeterminate/missing tests -> disease present/absent -> accuracy analysis.",
    },
    "comparative_diagnostic_accuracy": {
        "label": "Comparative diagnostic accuracy study",
        "reporting": ["STARD 2015", "STARD-AI when applicable"],
        "bias_tools": ["QUADAS-3 plus QUADAS-C for the comparative accuracy question"],
        "methods": ["prefer fully paired or randomized comparative designs", "same reference standard and threshold handling", "within-person comparison", "reader/order effects", "paired confidence intervals"],
        "table": "Describe the shared participant spectrum and test completion pattern. Show paired/unpaired structure, reference standard, order, reader, device, and indeterminate results.",
        "flow": "Common eligibility -> index tests A/B -> reference standard -> paired completeness -> comparative accuracy analysis.",
    },
    "prediction_model_development": {
        "label": "Clinical prediction model development",
        "reporting": ["TRIPOD+AI for regression or AI prediction models"],
        "bias_tools": ["PROBAST+AI"],
        "methods": ["effective sample-size/event planning", "bootstrap or repeated resampling for optimism", "penalization/shrinkage", "calibration and discrimination", "decision-curve analysis when clinically relevant", "temporal/geographic external validation"],
        "table": "Describe development and validation cohorts, predictor timing, outcome events, follow-up, missingness, site/time split, and case mix. Do not use PSM as a generic model-bias correction.",
        "flow": "Source data -> prediction time zero -> eligible observations/events -> development -> internal validation -> external validation.",
    },
    "prediction_model_validation": {
        "label": "External validation or updating of a clinical prediction model",
        "reporting": ["TRIPOD+AI"],
        "bias_tools": ["PROBAST+AI"],
        "methods": ["locked-model evaluation", "calibration-in-the-large and slope", "discrimination", "clinical utility", "recalibration/model updating declared separately", "transportability subgroups"],
        "table": "Describe the external-validation cohort against the intended-use population, with events, predictor availability, missingness, case mix, and site/time differences.",
        "flow": "External source -> eligibility -> locked model inputs -> outcome ascertainment -> performance -> optional recalibration/update.",
    },
    "systematic_review_meta_analysis": {
        "label": "Systematic review and meta-analysis",
        "reporting": ["PRISMA 2020", "PRISMA-P for protocols", "PRISMA-DTA for diagnostic reviews", "TRIPOD-SRMA for prediction-model reviews"],
        "bias_tools": ["RoB 2 for randomized trials", "ROBINS-I for non-randomized interventions", "QUADAS-3/QUADAS-C for diagnostic accuracy", "PROBAST+AI for prediction models", "ROBIS for review-level bias"],
        "methods": ["protocol and comprehensive search", "duplicate screening/extraction", "design-specific risk of bias", "appropriate random-effects or hierarchical model", "heterogeneity and certainty assessment"],
        "table": "Use a study-characteristics table, not a patient baseline Table 1. Include design, population, intervention/exposure/test/model, comparator, outcomes, follow-up, and risk of bias.",
        "flow": "Records identified -> deduplicated -> screened -> full text -> excluded with reasons -> included studies -> synthesis sets.",
    },
    "systematic_review_narrative": {
        "label": "Systematic review with structured narrative synthesis",
        "reporting": ["PRISMA 2020", "PRISMA-P for protocols", "SWiM when synthesis without meta-analysis applies"],
        "bias_tools": ["Design-specific risk-of-bias tool", "ROBIS for review-level bias"],
        "methods": ["protocol and comprehensive search", "duplicate screening/extraction", "structured grouping and synthesis", "transparent direction/strength of effects", "heterogeneity and certainty assessment"],
        "table": "Use a study-characteristics table and structured synthesis groups; do not force statistically incompatible studies into a pooled estimate.",
        "flow": "Records identified -> deduplicated -> screened -> full text -> included studies -> structured synthesis groups.",
    },
    "scoping_review": {
        "label": "Scoping review",
        "reporting": ["PRISMA-ScR", "PRISMA-P or an appropriate protocol framework"],
        "bias_tools": ["Critical appraisal is optional and must match the review objective when performed"],
        "methods": ["broad eligibility and systematic search", "iterative charting", "concept/context mapping", "evidence-gap characterization", "transparent stakeholder consultation when used"],
        "table": "Use an evidence-map or study-characteristics table covering concepts, populations, settings, designs, interventions/tests/models, and outcome domains.",
        "flow": "Records identified -> deduplicated -> screened -> full text -> included sources -> evidence map.",
    },
    "qualitative_study": {
        "label": "Qualitative study",
        "reporting": ["SRQR", "COREQ for interviews/focus groups"],
        "bias_tools": ["reflexivity, sampling, credibility, and transferability appraisal"],
        "methods": ["purposeful/theoretical sampling", "reflexivity", "audit trail", "triangulation or member reflection as appropriate", "saturation/information-power rationale"],
        "table": "Use participant and context characteristics relevant to transferability; do not add inferential balance tests.",
        "flow": "Sampling frame -> approached -> consented -> data collected -> excluded/withdrawn -> analyzed.",
    },
    "economic_evaluation": {
        "label": "Health economic evaluation",
        "reporting": ["CHEERS 2022", "CHEERS-AI when applicable"],
        "bias_tools": ["model-input and structural-uncertainty appraisal"],
        "methods": ["perspective and time horizon", "cost and outcome valuation", "discounting", "probabilistic sensitivity analysis", "scenario and structural uncertainty"],
        "table": "Describe the target population, comparator, resource use, costs, utilities, time horizon, and model inputs rather than a conventional balance table alone.",
        "flow": "Population/comparators -> resource and outcome inputs -> model states -> base case -> uncertainty analyses.",
    },
}


QUESTION_BANK = {
    "primary_aim": {
        "question": "这项研究最主要想回答哪一类问题？",
        "options": [
            ["intervention_effect", "干预/系统是否改善临床或工作流结局"],
            ["association_risk", "暴露因素与风险/相关性"],
            ["diagnostic_accuracy", "某项检查或AI的诊断准确性"],
            ["prediction", "开发或验证个体风险预测模型"],
            ["evidence_synthesis", "汇总多篇研究证据"],
            ["qualitative", "理解体验、行为或实施机制"],
            ["economic", "成本效果、成本效用或投资回报"],
        ],
    },
    "rollout_structure": {
        "question": "干预或系统将以什么方式上线/分配？",
        "options": [
            ["randomized_individual", "个体随机分配"],
            ["randomized_cluster", "科室/病区/医院集群随机"],
            ["randomized_staggered", "按随机顺序分阶段上线"],
            ["fixed_date_series", "固定日期全量上线，前后都有多个连续时间点"],
            ["nonrandom_staggered", "非随机分阶段上线"],
            ["single_pre_post", "只有上线前后各一次或少量汇总"],
            ["no_intervention", "没有主动干预，仅观察自然暴露"],
        ],
    },
    "concurrent_control": {
        "question": "能否获得同期未上线或未暴露的可比对照序列？",
        "options": [
            ["yes", "有同期对照科室/病区/医院，并可获得相同时间频率数据"],
            ["partial", "只有部分时期或不完全可比的同期对照"],
            ["no", "没有同期对照，只能使用本机构历史序列"],
        ],
    },
    "data_source": {
        "question": "主要数据从哪里获得？",
        "options": [
            ["prospective_primary", "前瞻性专门采集"],
            ["retrospective_ehr", "回顾性电子病历/信息系统日志"],
            ["registry_claims", "登记、理赔或其他常规收集数据"],
            ["mixed_prospective_routine", "常规数据加前瞻性补充采集"],
            ["published_literature", "已发表文献"],
        ],
    },
    "primary_outcome_family": {
        "question": "必须优先聚焦的主要结局是哪一类？",
        "options": [
            ["clinical_safety", "患者安全/不良事件"],
            ["clinical_quality", "诊疗质量或规范一致性"],
            ["workflow", "效率、时效、工作量或资源利用"],
            ["accuracy", "诊断准确性"],
            ["prediction_performance", "预测性能与临床效用"],
            ["economic", "成本、净收益或成本效果"],
        ],
    },
    "analysis_unit": {
        "question": "主要分析单位是什么？",
        "options": [
            ["patient", "患者"], ["encounter", "住院/门诊就诊"], ["event", "质控问题/不良事件/预警"],
            ["clinician", "临床人员"], ["cluster", "科室/病区/医院"], ["time_period", "日/周/月等时间点"],
        ],
    },
    "diagnostic_comparison": {
        "question": "诊断研究是在同一批受试者中比较两个或以上的指数试验吗？",
        "options": [["paired", "是，尽量让同一受试者接受全部指数试验"], ["unpaired", "不是，试验分配给不同受试者"], ["single_test", "只评价一个指数试验"]],
    },
    "prediction_stage": {
        "question": "预测模型研究处于哪个阶段？",
        "options": [["development", "模型开发并做内部验证"], ["external_validation", "使用独立时空/机构数据做外部验证"], ["updating", "外部验证并更新/再校准"], ["impact", "评价模型投入临床后的患者或工作流影响"]],
    },
    "review_target": {
        "question": "证据综合主要汇总哪类研究？",
        "options": [["intervention", "干预效果"], ["diagnostic", "诊断准确性"], ["prediction", "预测模型"], ["exposure", "暴露/风险因素"], ["qualitative", "定性证据"]],
    },
    "review_scope": {
        "question": "这次证据综合希望达到哪种主要目的？",
        "options": [
            ["quantitative_meta", "定量合并可比研究的总体效应或准确性"],
            ["systematic_narrative", "系统检索与评价，但因异质性采用结构化叙述综合"],
            ["scoping", "广泛梳理应用场景、概念、结局与证据缺口"],
        ],
    },
}


def norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def has_ai_intent(text):
    """Detect an actual AI-healthcare intent without matching words like 'paired'."""
    normalized = norm(text)
    explicit_terms = [
        "llm", "large language model", "artificial intelligence", "machine learning",
        "deep learning", "智能体", "人工智能", "机器学习", "深度学习", "ai系统",
        "ai-assisted", "ai-enabled", "ai-driven",
    ]
    return any(term in normalized for term in explicit_terms) or bool(re.search(r"\bai\b", normalized))


def inferred_answers(spec):
    proposal = norm(spec.get("proposal") or spec.get("research_question") or spec.get("title"))
    inferred = {}
    if any(term in proposal for term in ["荟萃", "meta-analysis", "systematic review", "系统综述", "多篇文献", "汇总文献"]):
        inferred["primary_aim"] = "evidence_synthesis"
        if any(term in proposal for term in ["干预", "决策支持", "改善", "患者结局", "effect"]):
            inferred["review_target"] = "intervention"
        if any(term in proposal for term in ["荟萃", "meta-analysis", "合并效应"]):
            inferred["review_scope"] = "quantitative_meta"
    elif any(term in proposal for term in ["准确性", "accuracy", "敏感度", "特异度", "参考标准"]):
        inferred["primary_aim"] = "diagnostic_accuracy"
    elif any(term in proposal for term in ["预测", "prediction", "风险模型", "prognostic", "c-index", "校准"]):
        inferred["primary_aim"] = "prediction"
    elif any(term in proposal for term in ["引入", "上线", "实施", "intervention", "deploy", "deployment"]) and any(term in proposal for term in ["比较", "对比", "变化", "改善", "收益", "effect"]):
        inferred["primary_aim"] = "intervention_effect"
    elif any(term in proposal for term in ["相关性", "association", "风险因素", "risk factor"]):
        inferred["primary_aim"] = "association_risk"
    if any(term in proposal for term in ["回顾性", "retrospective"]) and any(term in proposal for term in ["电子病历", "ehr", "信息系统", "影像", "routine data"]):
        inferred["data_source"] = "retrospective_ehr"
    elif any(term in proposal for term in ["登记", "registry", "claims", "理赔"]):
        inferred["data_source"] = "registry_claims"
    elif any(term in proposal for term in ["前瞻性", "prospective"]) and any(term in proposal for term in ["专门采集", "primary collection", "研究采集"]):
        inferred["data_source"] = "prospective_primary"
    return inferred


def effective_answers(spec):
    answers = dict(inferred_answers(spec))
    answers.update(spec.get("answers") or spec.get("intake_answers") or {})
    return answers


def add(scores, design, weight, evidence):
    scores.setdefault(design, {"score": 0.0, "evidence": []})
    scores[design]["score"] += weight
    scores[design]["evidence"].append(evidence)


def classify(spec):
    proposal = norm(spec.get("proposal") or spec.get("research_question") or spec.get("title"))
    answers = effective_answers(spec)
    scores = {}
    aim = answers.get("primary_aim")
    rollout = answers.get("rollout_structure")
    control = answers.get("concurrent_control")
    source = answers.get("data_source")

    if any(term in proposal for term in ["质控", "quality improvement", "workflow", "工作流", "预警", "cdss", "decision support"]):
        add(scores, "interrupted_time_series", 2.0, "proposal describes a workflow or quality intervention")
        add(scores, "controlled_interrupted_time_series", 2.0, "proposal describes a workflow or quality intervention")
        add(scores, "difference_in_differences", 1.0, "implementation effect may require a concurrent comparison")
    if has_ai_intent(proposal):
        add(scores, "interrupted_time_series", 0.5, "AI deployment is an intervention event")
        add(scores, "controlled_interrupted_time_series", 0.5, "AI deployment is an intervention event")
    if any(term in proposal for term in ["准确性", "accuracy", "敏感度", "特异度", "reference standard", "参考标准"]):
        add(scores, "diagnostic_accuracy", 4.0, "accuracy intent and reference-standard language")
    if any(term in proposal for term in ["预测", "prediction", "风险模型", "prognostic", "c-index", "calibration", "校准"]):
        add(scores, "prediction_model_development", 4.0, "individual prediction intent")
    if any(term in proposal for term in ["荟萃", "meta-analysis", "systematic review", "系统综述", "多篇文献"]):
        add(scores, "systematic_review_meta_analysis", 5.0, "evidence-synthesis intent")
    if any(term in proposal for term in ["相关性", "association", "风险因素", "risk factor"]):
        add(scores, "descriptive_observational", 3.0, "association/risk-factor intent")
    if any(term in proposal for term in ["成本效果", "cost-effectiveness", "成本效用", "roi", "投资回报"]):
        add(scores, "economic_evaluation", 3.0, "economic-evaluation intent")
    if any(term in proposal for term in ["访谈", "焦点小组", "体验", "qualitative"]):
        add(scores, "qualitative_study", 4.0, "qualitative intent")

    if aim == "intervention_effect":
        for design in ["controlled_interrupted_time_series", "interrupted_time_series", "difference_in_differences", "randomized_controlled_trial"]:
            add(scores, design, 1.0, "user selected intervention-effect aim")
    elif aim == "association_risk":
        add(scores, "descriptive_observational", 4.0, "user selected association/risk aim")
        add(scores, "observational_causal", 1.0, "causal interpretation remains a possible refinement")
    elif aim == "diagnostic_accuracy":
        add(scores, "diagnostic_accuracy", 6.0, "user selected diagnostic-accuracy aim")
    elif aim == "prediction":
        add(scores, "prediction_model_development", 6.0, "user selected prediction aim")
    elif aim == "evidence_synthesis":
        add(scores, "systematic_review_meta_analysis", 7.0, "user selected evidence synthesis")
    elif aim == "qualitative":
        add(scores, "qualitative_study", 7.0, "user selected qualitative aim")
    elif aim == "economic":
        add(scores, "economic_evaluation", 7.0, "user selected economic aim")

    if rollout == "randomized_individual":
        add(scores, "randomized_controlled_trial", 8.0, "individual randomization")
    elif rollout == "randomized_cluster":
        add(scores, "randomized_controlled_trial", 7.0, "cluster randomization")
    elif rollout == "randomized_staggered":
        add(scores, "stepped_wedge_cluster_rct", 10.0, "randomized staggered rollout")
    elif rollout == "fixed_date_series":
        add(scores, "interrupted_time_series", 8.0, "fixed intervention point with repeated observations")
        if control == "yes":
            add(scores, "controlled_interrupted_time_series", 12.0, "concurrent repeated control series")
    elif rollout == "nonrandom_staggered":
        add(scores, "difference_in_differences", 8.0, "non-random staggered rollout")
    elif rollout == "single_pre_post":
        add(scores, "interrupted_time_series", -2.0, "insufficient repeated observations for a defensible ITS")
        add(scores, "descriptive_observational", 2.0, "simple pre-post description")
    elif rollout == "no_intervention":
        add(scores, "descriptive_observational", 5.0, "natural exposure without intervention assignment")

    if control == "yes" and rollout == "fixed_date_series":
        add(scores, "controlled_interrupted_time_series", 5.0, "concurrent control available")
    elif control == "no" and rollout == "fixed_date_series":
        add(scores, "interrupted_time_series", 4.0, "no concurrent control")
    if source in {"retrospective_ehr", "registry_claims"}:
        for design in scores:
            scores[design]["evidence"].append("routine-data source triggers RECORD overlay")

    diagnostic_comparison = answers.get("diagnostic_comparison")
    if diagnostic_comparison in {"paired", "unpaired"}:
        add(scores, "comparative_diagnostic_accuracy", 14.0, f"comparative diagnostic design: {diagnostic_comparison}")
    prediction_stage = answers.get("prediction_stage")
    if prediction_stage in {"external_validation", "updating"}:
        add(scores, "prediction_model_validation", 10.0, f"prediction stage: {prediction_stage}")
    review_scope = answers.get("review_scope")
    if review_scope == "quantitative_meta":
        add(scores, "systematic_review_meta_analysis", 10.0, "quantitative synthesis objective")
    elif review_scope == "systematic_narrative":
        add(scores, "systematic_review_narrative", 14.0, "structured systematic review without meta-analysis")
    elif review_scope == "scoping":
        add(scores, "scoping_review", 14.0, "evidence mapping and gap-identification objective")

    if not scores:
        add(scores, "descriptive_observational", 0.5, "fallback pending clarification")
    positive = {key: value for key, value in scores.items() if value["score"] > 0}
    total = sum(value["score"] for value in positive.values()) or 1.0
    ranked = []
    for design, value in positive.items():
        ranked.append({
            "design_id": design,
            "label": DESIGNS[design]["label"],
            "confidence": round(value["score"] / total, 3),
            "evidence": list(dict.fromkeys(value["evidence"])),
        })
    ranked.sort(key=lambda item: item["confidence"], reverse=True)
    return ranked[:5]


def next_question(spec, candidates):
    answers = effective_answers(spec)
    if "primary_aim" not in answers:
        return {"id": "primary_aim", **QUESTION_BANK["primary_aim"]}
    aim = answers["primary_aim"]
    if aim == "intervention_effect" and "rollout_structure" not in answers:
        return {"id": "rollout_structure", **QUESTION_BANK["rollout_structure"]}
    if aim == "intervention_effect" and answers.get("rollout_structure") in {"fixed_date_series", "nonrandom_staggered"} and "concurrent_control" not in answers:
        return {"id": "concurrent_control", **QUESTION_BANK["concurrent_control"]}
    if aim == "diagnostic_accuracy" and "diagnostic_comparison" not in answers:
        return {"id": "diagnostic_comparison", **QUESTION_BANK["diagnostic_comparison"]}
    if aim == "prediction" and "prediction_stage" not in answers:
        return {"id": "prediction_stage", **QUESTION_BANK["prediction_stage"]}
    if aim == "evidence_synthesis" and "review_target" not in answers:
        return {"id": "review_target", **QUESTION_BANK["review_target"]}
    if aim == "evidence_synthesis" and "review_scope" not in answers:
        return {"id": "review_scope", **QUESTION_BANK["review_scope"]}
    if "data_source" not in answers:
        return {"id": "data_source", **QUESTION_BANK["data_source"]}
    if aim in {"intervention_effect", "association_risk", "diagnostic_accuracy", "prediction"} and "primary_outcome_family" not in answers:
        return {"id": "primary_outcome_family", **QUESTION_BANK["primary_outcome_family"]}
    if aim not in {"evidence_synthesis", "qualitative", "economic"} and "analysis_unit" not in answers:
        return {"id": "analysis_unit", **QUESTION_BANK["analysis_unit"]}
    return None


def guideline_overlays(spec, design_id):
    proposal = norm(spec.get("proposal"))
    answers = effective_answers(spec)
    overlays = []
    if any(term in proposal for term in ["质控", "quality improvement", "improvement"]):
        overlays.append("SQUIRE 2.0")
    if design_id in {"controlled_interrupted_time_series", "interrupted_time_series", "difference_in_differences"}:
        overlays.append("TREND")
    if answers.get("data_source") in {"retrospective_ehr", "registry_claims", "mixed_prospective_routine"}:
        overlays.append("RECORD")
    if design_id not in {"systematic_review_meta_analysis", "systematic_review_narrative", "scoping_review"} and (has_ai_intent(proposal) or any(term in proposal for term in ["decision support", "cdss"])):
        overlays.append("DECIDE-AI when this is an early-stage live clinical AI evaluation")
    return list(dict.fromkeys(overlays))


def triage(spec):
    candidates = classify(spec)
    question = next_question(spec, candidates)
    top = candidates[0]
    confirmed = spec.get("confirmed_design")
    if question:
        stage = "clarify"
        selected_id = top["design_id"]
    elif confirmed in DESIGNS:
        stage = "ready"
        selected_id = confirmed
    else:
        stage = "confirm"
        selected_id = top["design_id"]
    profile = DESIGNS[selected_id]
    return {
        "stage": stage,
        "ready_for_design": stage == "ready",
        "proposal": spec.get("proposal", ""),
        "inferred_answers": inferred_answers(spec),
        "candidates": candidates,
        "next_question": question,
        "confirmation_prompt": None if stage != "confirm" else f"建议主设计为 {top['label']}。是否确认采用该设计？",
        "recommended_design": {"design_id": selected_id, **profile},
        "guideline_overlays": guideline_overlays(spec, selected_id),
        "guardrail": "Reporting guidelines, risk-of-bias tools, and analysis methods are separate layers; do not use one as a substitute for another.",
    }


def render_markdown(result):
    lines = ["# Study Design Triage", "", f"Stage: {result['stage']}", "", "## Candidate designs", ""]
    for item in result["candidates"]:
        lines.append(f"- {item['label']}: {item['confidence']:.1%}")
    if result["next_question"]:
        question = result["next_question"]
        lines.extend(["", "## Next question", "", question["question"], ""])
        for value, label in question["options"]:
            lines.append(f"- `{value}`: {label}")
    elif result["confirmation_prompt"]:
        lines.extend(["", "## Confirm design", "", result["confirmation_prompt"]])
    else:
        profile = result["recommended_design"]
        lines.extend(["", "## Confirmed design", "", profile["label"], "", "### Reporting", ""])
        lines.extend([f"- {item}" for item in profile["reporting"] + result["guideline_overlays"]])
        lines.extend(["", "### Bias tools", ""] + [f"- {item}" for item in profile["bias_tools"]])
        lines.extend(["", "### Methods", ""] + [f"- {item}" for item in profile["methods"]])
        lines.extend(["", "### Table 1", "", profile["table"], "", "### Flow", "", profile["flow"]])
    lines.extend(["", f"> {result['guardrail']}", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    result = triage(spec)
    output = json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
