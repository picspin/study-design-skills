# Design-Specific Playbooks

Use this reference to connect Table 1, flowchart, grouping/matching, and sensitivity analyses for common high-impact biomedical designs.

## RWE Comparative Effectiveness

Output package:

- STROBE/RECORD-aligned attrition flowchart.
- Time-zero definition.
- Table 1 before and after matching/weighting or a clear post-design Table 1 plus supplementary pre-design balance.
- DAG-based confounder list.
- Matching/weighting algorithm transparency.
- Missing-data plan with MI and complete-case comparison when relevant.
- Sensitivity analyses for unmeasured confounding and design fragility.

Required design decisions:

- New-user versus prevalent-user design.
- Active comparator versus non-user comparator.
- Index date and grace period.
- Lookback window for covariates.
- Follow-up start and end.
- Outcome ascertainment window.
- Immortal time and depletion-of-susceptibles checks.

## Diagnostic Accuracy And Radiology

Output package:

- STARD-aligned participant/image flowchart.
- One-gate or two-gate design declaration.
- Table 1 by reference-standard status, index-test status, or analytic cohort.
- Bias audit for selection, spectrum, verification, and reference-standard bias.
- Sensitivity analyses for reader, device, site, threshold, and reference standard.

Required design decisions:

- Patient-level versus image/lesion-level unit.
- Consecutive sampling versus enriched case-control sampling.
- Blinding between index test, clinical data, and reference standard.
- Handling indeterminate index tests and missing reference standards.
- Reader adjudication and inter-rater reliability.

## Prediction Model, Prognosis, And Survival

Output package:

- TRIPOD+AI-aligned source-to-split flowchart.
- Table 1 by development, validation, and test cohort.
- Event count, censoring, and follow-up summary.
- Predictor missingness and imputation plan.
- Model type: Cox, penalized Cox, logistic, competing risk, ML, or other.
- Performance plan: C-index, calibration, decision curve, and external validation.

Required design decisions:

- Prediction time zero.
- Outcome horizon.
- Candidate predictor timing.
- Event-per-parameter or effective sample-size logic.
- Temporal/geographic/site split and leakage prevention.
- Clustered, repeated, or multi-modal data handling.

## AI Healthcare Workflow, CDSS, Triage, And Quality Improvement

Output package:

- ICAML-style AI workflow flowchart.
- Guideline cross-map: ICAML first, then DECIDE-AI, SQUIRE, STROBE/RECORD, CONSORT-AI, STARD-AI, or TRIPOD+AI only when design-appropriate.
- Table 1 by pre/post period, AI exposure, site/cluster, alert status, clinician action, or human-only versus human+AI condition.
- Endpoint hierarchy covering clinical quality, workflow performance, adoption, safety, and fairness.
- Bias audit for selection, workflow confounding, automation bias, alert fatigue, secular trends, verification bias, and drift.
- Sensitivity analyses for threshold, adoption/override, site/shift, ramp-up period, model version, and secular trend.

Required design decisions:

- AI role: silent reviewer, visible recommendation, alert, triage prioritizer, CDSS, autonomous action, documentation/summarization, or escalation tool.
- Unit of analysis: patient, encounter, order, image, message, alert, task, clinician, site, or shift.
- Workflow entry point and trigger criteria.
- Human-in-the-loop step and override pathway.
- Comparator: pre-AI, concurrent usual care, randomized/clustered control, stepped-wedge control, silent-mode comparison, or human-only review.
- Safety monitoring, adverse event adjudication, and fairness strata.

## RCT

Output package:

- CONSORT participant flowchart.
- Table 1 by randomized arm.
- Primary clinical endpoint and analysis population definitions.
- Missing outcome strategy and estimand.
- Harms/safety population if different from efficacy population.

Required design decisions:

- Parallel, cluster, factorial, crossover, non-inferiority, pragmatic, AI intervention, or other CONSORT extension.
- Randomization ratio and stratification/minimization factors.
- ITT, modified ITT, per-protocol, and safety population.
- Final clinical outcome and follow-up schedule.
- Missing outcome and protocol deviation handling.

## Manuscript-Ready Output Order

1. Study type and guideline mapping.
2. Time zero or randomization/prediction/index-test anchor.
3. Flowchart specification.
4. Table 1 shell and variable blocks.
5. Grouping/matching/weighting algorithm.
6. Missing-data plan.
7. Sensitivity-analysis matrix.
8. Journal-style footnotes and caption.
