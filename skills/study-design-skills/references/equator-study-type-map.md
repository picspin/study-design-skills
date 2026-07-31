# EQUATOR Study-Type Map For Table 1

Use this reference to map a biomedical study to a reporting guideline family and then infer what Table 1 must accomplish.

## Core Principle

Identify the design first. Table 1 should describe the population, groups, exposures, intervention arms, sampling frame, analytic set, or model-development split that the study actually uses. Do not let software defaults choose the scientific table.

## Broad Study Families

| Study family | Common guideline family | Table 1 purpose |
| --- | --- | --- |
| Randomized trial | CONSORT 2025; SPIRIT for protocols; CONSORT extensions for cluster, non-inferiority, harms, AI, pragmatic, routine-data, or other variants | Describe randomized groups and the analysis population without implying that significance tests validate randomization. |
| Observational study | STROBE; RECORD for routinely collected health data; TARGET for target-trial emulations; STREGA for genetic association extensions | Describe cohort assembly, exposure/treatment groups, confounding structure, missingness, and balance before and after design/weighting when relevant. |
| Real-world evidence | STROBE plus RECORD or domain extensions such as oncology RWE guidance | Make data provenance, eligibility, index date, lookback window, follow-up, care setting, and missingness visible. |
| Cohort study | STROBE | Describe baseline at cohort entry/index date, exposure groups, time zero, follow-up, and censoring-relevant variables. |
| Case-control study | STROBE | Describe cases and controls, matching variables, selection source, index/reference date, and exposure ascertainment. |
| Cross-sectional study | STROBE | Describe sampled population, survey design, weights, response/missingness, and outcome/exposure strata if used. |
| Diagnostic accuracy study | STARD; STARD-AI for AI diagnostic studies | Describe participants by disease/reference-standard status or test groups, spectrum of disease, setting, and timing between index and reference standard. |
| Prognostic or prediction model study | TRIPOD; TRIPOD+AI for AI/ML models; TRIPOD-LLM when applicable | Describe development, validation, and test cohorts; candidate predictors; outcomes; event counts; missingness; and site/time splits. |
| Medical AI evaluation | CONSORT-AI for randomized AI interventions; SPIRIT-AI for protocols; DECIDE-AI for early-stage clinical evaluation; TRIPOD+AI/STARD-AI by task | Describe clinical population, data source, model deployment context, sites, acquisition devices, data partitions, and fairness-relevant covariates. |
| AI healthcare workflow, CDSS, triage, quality improvement, or implementation | ICAML-style clinical AI implementation frame; cross-map to DECIDE-AI, SQUIRE, STROBE/RECORD, CONSORT-AI, STARD-AI, or TRIPOD+AI only when appropriate | Describe eligible clinical encounters, workflow entry point, AI trigger, AI output, clinician review/action/override, downstream workflow or clinical outcome, safety, adoption, and fairness. |
| Systematic review or meta-analysis | PRISMA; PRISMA-P for protocols; TRIPOD-SRMA for prediction model reviews | Usually create a study-characteristics table rather than patient-level Table 1. Include study design, population, intervention/exposure, outcomes, risk of bias, and follow-up. |
| Case report or case series | CARE; specialty extensions such as CARE-radiology | Use a clinical summary table or timeline rather than conventional group baseline Table 1. |
| Quality improvement study | SQUIRE | Describe setting, participants, context, intervention exposure, baseline process/outcome measures, and implementation periods. |
| Interrupted time series / controlled ITS | TREND for nonrandomized intervention reporting; SQUIRE 2.0 for healthcare improvement; RECORD for routine data; DECIDE-AI for early live AI decision support | Describe intervention/control series, repeated pre/post periods, baseline level and slope, clinical/workflow composition, volume, season, staffing, and outcome ascertainment. |
| Difference-in-differences / comparative panel | TREND plus STROBE; RECORD for routine data; SQUIRE 2.0 when framed as improvement | Describe intervention/control clusters before rollout, baseline outcome trends, composition, timing, spillovers, and cluster context. |
| Economic evaluation | CHEERS | Describe population, intervention/comparator, perspective, time horizon, resource-use inputs, costs, utilities, and model assumptions. |
| Qualitative research | SRQR; COREQ for interviews/focus groups | Use participant/context characteristics table: recruitment, setting, role, demographics, sampling, and data saturation, not inferential comparisons. |
| Mixed-methods study | Mixed methods reporting guidance plus design-specific guideline | Separate quantitative baseline table from qualitative participant/context table when needed. |
| Animal or preclinical study | ARRIVE | Describe animals, strain, sex, age, weight, allocation, housing, intervention groups, and baseline measures. |
| Clinical practice guideline | AGREE; RIGHT | Table 1 is usually a guideline panel, evidence base, or recommendation-characteristics table, not a patient baseline table. |

## EQUATOR Library Scope Reminder

The EQUATOR reporting-guideline library allows browsing by study type, clinical area, and report section. Treat the list above as a practical starting map, then search the EQUATOR library for specialty extensions when the research design is narrow, emerging, or journal-sensitive.

## Table 1 Implications By Design

### RCT

- Columns: intervention arms; optional overall column.
- Rows: eligibility-defining demographics, disease severity, baseline outcome, key prognostic variables, stratification/minimization variables, site/region if clinically relevant.
- Usually omit p values; include standardized differences only if required or if imbalance is substantively discussed.
- Footnote analysis set: randomized, intention-to-treat, modified intention-to-treat, safety, or per-protocol.
- Flowchart: assessed for eligibility, randomized, allocated, received intervention, lost to follow-up, discontinued, analyzed by arm.

### Observational/RWE

- Columns: exposure/treatment groups or analytic cohorts; optional pre-match/pre-weight and post-match/post-weight panels.
- Rows: confounders, proxies for disease severity, healthcare utilization, calendar time, site, data-source variables, outcome-risk factors.
- Include SMDs for balance, especially after matching/weighting.
- Footnote index date, lookback window, follow-up start, missingness, imputation, and weighting.
- Flowchart: source data, eligibility, time zero/index date, treatment assignment, baseline covariate availability, matching/weighting/trimming, follow-up, final analytic cohort.
- Sensitivity: MI versus complete-case, alternative matching/weighting, alternative confounder sets, negative controls, lag windows, E-value or quantitative bias analysis when appropriate.

### ITS, Controlled ITS, And DiD

- Columns/objects: intervention and control series, pre/post periods, or cluster rollout groups; add a time-series characteristics block rather than relying on a two-column balance table.
- Rows: patient/encounter mix, baseline outcome level and trend, observation frequency, volume/denominator, season, staffing, site, concurrent initiatives, measurement definition, data completeness.
- Analysis: segmented level/slope changes for ITS/CITS; group-by-time/event-study terms and pre-trend diagnostics for DiD.
- Bias control: autocorrelation, seasonality, co-interventions, intervention-date specification, ramp-up, composition change, spillover, outcome-measurement change, and unaffected outcomes/series.
- PSM is optional and secondary only when it addresses a clearly defined compositional causal contrast; it does not replace time-series identification.

### Diagnostic/Prognostic/AI

- Columns: disease/reference-standard status, outcome/event status, development/validation/test cohort, site/time split, or model exposure group.
- Rows: spectrum variables, acquisition device/protocol, clinical setting, disease severity, candidate predictors, outcome/event count.
- Emphasize event counts and data partitions over p values.
- Footnote leakage prevention, repeated measures, site clustering, and missing predictors.
- Flowchart: one-gate/two-gate sampling for diagnostic studies; source-to-development/validation/test split for prediction and AI studies.
- Sensitivity: kappa/reader agreement, device/site/protocol sensitivity, verification/reference-standard sensitivity, C-index/calibration/external validation for prediction.
- Appraisal: use QUADAS-3 for diagnostic accuracy risk-of-bias/applicability assessment; use QUADAS-C alongside QUADAS-3 for within-study comparative accuracy questions. Use PROBAST+AI for prediction models.
- Never treat propensity matching as a generic correction for diagnostic spectrum bias or prediction-model overfitting.

### AI Healthcare Workflow And ICAML-Style Studies

- Columns: pre-AI versus post-AI, AI-exposed versus unexposed, intervention versus control site, silent-mode versus live-mode, human-only versus human+AI, or accepted versus overridden recommendation.
- Rows: patient/encounter characteristics, clinical severity, site/department/shift, workflow volume, AI input availability, trigger criteria, model version, threshold, clinician role, action/override, safety and fairness strata.
- Flowchart: eligible clinical stream, workflow entry point, AI trigger, AI output generated, output shown, clinician action/override, downstream action, safety/outcome ascertainment, final analyzed unit.
- Sensitivity: threshold, accepted-only versus intention-to-expose, ramp-up exclusion, site/shift subgroup, secular trend, model version/drift, safety adjudication, fairness strata.
- Do not default to TRIPOD if the study evaluates workflow or implementation impact rather than prediction-model development/validation.

### Qualitative/Mixed Methods

- Columns: participant group, site, role, sampling stratum, or overall.
- Rows: participant characteristics relevant to transferability.
- Avoid inferential tests unless a defined quantitative component needs them.

### Protocols

- Use planned baseline table shells, not fabricated results.
- Include planned variables, definitions, coding, units, data source, collection time point, and planned summary statistics.
