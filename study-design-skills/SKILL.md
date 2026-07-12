---
name: study-design-skills
description: Use when a biomedical research idea must be clarified, classified, designed, computed, exported, reviewed, scored, or journal-targeted, including interactive study-type triage, Table 1, participant flow, bias control, RCT, ITS/CITS, observational/RWE, diagnostic, prediction, evidence-synthesis, AI healthcare, and CSV/XLSX/HTML deliverables.
---

# Study Design Skills

## Overview

First converge from a broad research intention to a confirmed study design. Then design the study architecture, Table 1 or study-characteristics table, participant/study flow, design-specific bias controls, validation or robustness strategy, and final scoring report as one reporting unit. Do not let a familiar method such as PSM, MI, sensitivity analysis, or random train/test splitting determine the design.

Default to the PDBC role: act as a research methods coach, academic writing advisor, and study design reviewer. Prefer transparent reporting, reproducible statistical choices, and top-journal table conventions over decorative formatting.

## When To Use

Use this skill for requests such as:

- Create Table 1 for an RCT, cohort, case-control, cross-sectional, registry, real-world evidence, diagnostic accuracy, prognostic model, medical AI, qualitative mixed-methods, economic evaluation, or protocol manuscript.
- Create an RCT CONSORT flow diagram, STROBE/RECORD attrition flowchart, diagnostic accuracy STARD flowchart, prediction-model cohort split diagram, or AI dataset flow diagram.
- Design AI healthcare studies for clinical quality improvement, workflow optimization, triage, CDSS, AI-assisted diagnosis, care escalation, alerting, human-in-the-loop decision support, or deployment evaluation under an ICAML-style clinical AI implementation frame.
- Convert a messy baseline variable list into a publication-ready Table 1 shell.
- Decide whether to show p values, standardized mean differences, weighted summaries, missingness columns, subgroup columns, cohort flow denominators, E-values, multiple-imputation sensitivity analyses, or matched/weighted cohorts.
- Design propensity-score matching, weighting, overlap weighting, exact matching, Mahalanobis matching, full matching, entropy balancing, or other grouping algorithms with transparent causal covariate selection.
- Match Table 1 style to Nature, JAMA, Lancet, Cell, NEJM, Circulation, JCO, Radiology, or similar biomedical journals.
- Review a draft Table 1 for reporting-guideline mismatch, statistical misuse, missing denominators, unclear units, or inappropriate comparisons.
- Score generated study designs, enrollment plans, flowcharts, Table 1 shells, statistical plans, and journal-fit against a 10-point JCR Top-1 medicine benchmark.
- Generate Python `tableone`, R `tableone`, R `table1`, spreadsheet, Markdown, LaTeX, HTML, DOCX, or manuscript-ready table specifications.

## Workflow

1. Run the intake gate before generating study artifacts.
   - Load `references/study-intent-triage.md` whenever the user supplies an idea, proposal, broad objective, or uncertain study label.
   - Infer up to three candidate designs with uncertainty and evidence paths.
   - Ask exactly one unresolved question at a time. Offer concise options and allow free text; never dump a long questionnaire.
   - Prioritize questions about scientific aim, allocation/rollout and time structure, concurrent comparator, prospective/retrospective data source, primary outcome family, and analysis unit.
   - Narrow an overbroad objective to one primary outcome family; move other aims to secondary outcomes.
   - Present the recommended design and closest alternative, explain the discriminator, and obtain explicit confirmation.
   - Before confirmation, output only the triage state and next question. Do not fabricate a final Table 1, flowchart, analysis plan, or benchmark score.
   - Use `scripts/classify_study.py` for a deterministic first-pass triage. Treat it as an explainable weighted knowledge graph, not a validated neural classifier.

2. Separate question, design, reporting, appraisal, and analysis layers.
   - Scientific question: intervention effect, association/risk, diagnostic accuracy, individual prediction, evidence synthesis, qualitative mechanism, or economic value.
   - Primary design: RCT/cluster/stepped wedge, ITS/CITS, DiD, observational cohort/case-control/cross-sectional, diagnostic accuracy, prediction development/validation, systematic review, qualitative, or economic evaluation.
   - Reporting guideline: EQUATOR statements such as CONSORT, STROBE/RECORD, STARD, TRIPOD+AI, PRISMA, SQUIRE, TREND, DECIDE-AI, CHEERS, SRQR/COREQ.
   - Bias/appraisal tool: RoB 2, ROBINS-I/ROBINS-E, QUADAS-3/QUADAS-C, PROBAST+AI, ROBIS.
   - Analysis method: randomization, segmented regression, DiD/event study, DAG/weighting, paired accuracy analysis, internal/external validation, or hierarchical meta-analysis.
   - Never present a reporting statement as if it corrects bias, or a risk-of-bias checklist as if it were the statistical model.

3. Identify the confirmed research design before choosing the table layout.
   - Load `references/equator-study-type-map.md` when the study type or reporting guideline is unclear.
   - Load `references/design-method-matrix.md` to select the design-specific Table 1, flow, bias-control, and validation bundle.
   - Map broad study families to the relevant reporting guideline family: CONSORT/SPIRIT for trials, STROBE/RECORD/TARGET for observational and real-world evidence, STARD for diagnostic accuracy, TRIPOD/TRIPOD+AI for prediction models, PRISMA for evidence syntheses, CARE for case reports, SQUIRE for quality improvement, CHEERS for economic evaluations, ARRIVE for animal studies, and AGREE/RIGHT for guidelines.
   - For AI healthcare implementation, workflow optimization, triage, CDSS, and AI-enabled quality-improvement studies, load `references/ai-healthcare-icaml.md` and do not force the study into TRIPOD, CONSORT, or STARD unless its primary question truly is prediction-model reporting, randomized intervention reporting, or diagnostic accuracy.
   - State when Table 1 is not the main reporting object, such as systematic reviews where study-characteristics tables are usually more appropriate than patient baseline tables.

4. Define the table estimand and comparison columns.
   - Use randomized arms for explanatory RCTs.
   - Use exposure, treatment, disease status, case/control status, outcome status, cohort, registry source, site, time period, or model-development split only when scientifically justified.
   - Include an Overall column when it helps interpret the analytic population; omit it when it creates clutter or conflicts with journal style.
   - Preserve denominators at the column level and report whether percentages use non-missing, column, row, weighted, or full-analysis denominators.
   - For RWE and longitudinal observational designs, explicitly define time zero, index date, lookback window, follow-up start, censoring, and at-risk set before creating Table 1.
   - For ITS/CITS, describe patient/encounter composition and workflow context by series/period, plus baseline level, slope, volume, season, staffing, and repeated time-point structure. Do not reduce the design to one pre and one post column.
   - For prediction studies, use development/internal/external validation cohorts with outcome-event counts, predictor timing, missingness, calibration context, and site/time provenance. Do not add PSM by default.
   - For systematic reviews, create a study-characteristics table rather than a patient baseline Table 1.

5. Design the flowchart before finalizing Table 1 denominators.
   - Load `references/flowchart-design.md` for flowchart templates and attrition logic.
   - Make every exclusion and analytic-set transition visible: source population, eligibility, exclusions, exposure/treatment assignment, matching/weighting, missingness exclusions, follow-up, outcome ascertainment, and final analysis set.
   - For STROBE/RECORD RWE, use a funnel-style attrition diagram and warn about selection bias whenever exclusions occur after exposure assignment, after outcome availability, or due to missing data.
   - For CONSORT RCTs, preserve allocation, follow-up, and analysis nodes by randomized arm.
   - For STARD/Radiology studies, distinguish one-gate versus two-gate sampling and show index-test and reference-standard completion.
   - For prediction/AI studies, show source data, exclusions, unit of analysis, leakage controls, development/validation/test splits, and external validation.
   - For ICAML-style AI healthcare workflow studies, show eligible clinical encounters, workflow entry point, AI eligibility/trigger, AI output generation, human review, action taken or overridden, downstream workflow outcome, safety review, and final analyzed episodes.
   - For ITS/CITS/DiD, show intervention/control source streams, common eligibility and outcome definitions, repeated pre-periods, intervention/rollout and ramp-up, repeated post-periods, excluded time points, and final analytic series.

6. Classify variables and summary statistics.
   - Load `references/table1-statistical-decisions.md` before computing or specifying summaries.
   - Continuous approximately symmetric variables: mean (SD).
   - Continuous skewed variables: median (IQR), and consider median (range) only when the field expects it.
   - Categorical variables: n (%), with explicit handling of binary variables and multi-level categories.
   - Time-to-event follow-up: median follow-up (IQR or range), person-time, censoring, or reverse Kaplan-Meier estimates when available.
   - Missingness: show missing n (%) when material, differential, or required for transparency.

7. Select only design-appropriate bias controls.
   - Load `references/design-method-matrix.md` first; load `references/causal-design-matching.md` only for a confirmed causal observational contrast.
   - RCT: randomization, concealment, blinding, ITT/estimand, missing outcome and harms.
   - ITS/CITS: segmented regression, level/slope, autocorrelation, seasonality, intervention timing, co-interventions, ramp-up, control series and falsification checks.
   - DiD/event study: pre-trends, leads/lags, cluster inference, spillover and treatment-timing assumptions.
   - Diagnostic accuracy: one-gate sampling, reference standard, blinding, verification, thresholds, paired/randomized test comparison; use QUADAS-3 and, for comparative questions, QUADAS-C alongside it in appraisal contexts.
   - Prediction: sample-size/event logic, bootstrap/resampling, shrinkage, calibration, discrimination, decision curves, and temporal/geographic/site external validation; use PROBAST+AI.
   - Evidence synthesis: protocol, comprehensive search, duplicate selection/extraction, design-specific risk-of-bias tool, appropriate synthesis model, heterogeneity and certainty.
   - Use PSM/weighting only when a causal observational estimand and defensible time zero justify it.

8. Specify matching, weighting, and causal covariate rules when applicable.
   - Load `references/causal-design-matching.md` for DAG, PSM, matching, weighting, and balance guidance.
   - Use clinical prior knowledge and DAGs to select confounders that affect exposure and outcome.
   - Do not include intermediates, post-index variables, post-outcome variables, colliders, consequences of treatment, or variables measured after time zero in propensity-score models.
   - Report the matching/weighting algorithm transparently: estimand, covariates, PS model, caliper, ratio, replacement, exact constraints, trimming, common support, software, seed, discarded participants, and post-design balance.

9. Choose inferential and balance columns cautiously.
   - For randomized trials, usually avoid baseline significance testing; prefer no p values or include only if journal/statistical analysis plan explicitly requires them.
   - For NEJM, Lancet, JAMA, and many high-impact clinical journals, default to no baseline p values in RCT Table 1 and RWE balance tables; use SMDs for balance, with SMD <0.1 as a common descriptive target rather than proof that confounding is eliminated.
   - For observational studies and real-world evidence, prefer standardized mean differences for baseline balance, especially after propensity score matching, weighting, or overlap weighting.
   - Use p values only when the comparison has a clear descriptive purpose and does not imply causal imbalance testing.
   - For weighted cohorts, report weighted summaries and SMDs; avoid mixing unweighted counts and weighted percentages without footnotes.

10. Specify missing-data, validation, and robustness expectations.
   - Load `references/sensitivity-analyses.md` when the study uses missing data methods, causal inference, diagnosis, prediction, RWE, or top-journal submission.
   - For missing baseline covariates, prefer a prespecified multiple-imputation plan when missingness is material and plausible missing-at-random assumptions can be defended.
   - Compare imputed versus complete-case or non-imputed results in sensitivity analyses; interpret differences clinically and directionally, not only by p value.
   - Consider E-values for unmeasured confounding in observational causal claims when compatible with the effect measure and audience.
   - Use multiple-model cross-checks when the estimate is design-sensitive: alternative covariate sets, matching/weighting algorithms, outcome models, competing risk approaches, negative controls, lag windows, and trimming rules.
   - For AI healthcare workflow studies, include alert-threshold sensitivity, workflow adoption sensitivity, clinician override analysis, subgroup/fairness checks, pre-post secular-trend checks, interrupted time-series or stepped-wedge robustness when applicable, and safety monitoring for automation bias.
   - Do not require the same sensitivity-analysis checklist for every design. Prediction studies primarily need optimism correction and internal/external validation; RCTs need estimand, missing-outcome, adherence and harms analyses; diagnostic studies need threshold, verification, reader/device and reference-standard checks.

11. Apply target journal style.
   - Load `references/journal-style-profiles.md` when a journal, family, or high-impact style is specified.
   - Favor dense, transparent, footnote-rich clinical style for JAMA, Lancet, NEJM, Circulation, JCO, and Radiology.
   - Favor compact, minimal, supplement-aware style for Nature, Cell, and Science-family articles.
   - Keep top-level headings concise and make units, transformations, and denominators visible.

12. Produce the scoring report after generating the design artifacts.
   - Load `references/benchmark-scoring.md` before finalizing any generated study design package.
   - Score against a 10-point JCR Top-1 medicine benchmark unless the user specifies a specialty benchmark, such as top oncology, radiology, cardiology, digital health, or clinical informatics journal.
   - Treat the benchmark as an editorial and methodological standard, not a promise of publication probability.
   - Provide total score, domain scores, major strengths, critical blockers, fix priorities, and an estimated post-revision ceiling.
   - Make the scoring report explicitly evaluate design-plan fit, enrollment/flowchart transparency, Table 1 adequacy, statistical/sensitivity-analysis rigor, reporting-guideline compliance, and target-journal style match.

13. Produce one output or a synchronized package.
   - Table design memo: study type, guideline, column logic, variable blocks, statistics, inferential choices, missingness policy, footnotes.
   - Flowchart specification: nodes, transitions, denominators, exclusion reasons, bias warnings, and Mermaid or manuscript-ready diagram text.
   - Study design blueprint: clinical workflow, AI intervention, comparator, unit of allocation/analysis, time anchor, endpoints, safety outcomes, adoption metrics, and reporting guideline.
   - Matching/grouping plan: time zero, exposure assignment, DAG covariates, algorithm, diagnostics, and reporting template.
   - Empty Table 1 shell: publication-ready rows and columns with placeholders.
   - Computation plan: Python/R/spreadsheet commands, package choices, flowchart data audit, and validation checks.
   - Review report: prioritized issues, fixes, and rewritten table caption/footnotes.
   - Benchmark scoring report: 10-point JCR Top-1 medicine score, subdomain scores, evidence-based rationale, and revision priorities.
   - Data deliverables: UTF-8 CSV Table 1, formatted XLSX workbook, self-contained HTML report, and Markdown memo generated from the same table rows and journal-fit results.

14. Prefer real files over Markdown-only output when the user requests a deliverable.
   - With patient-level CSV/XLSX data, compute Table 1 using `scripts/generate_study_package.py` or `scripts/design_study.py --out-dir`.
   - Without patient-level data, generate a publication-ready shell with real column headers and blank cells in CSV/XLSX/HTML.
   - Keep CSV flat and machine-readable. Put presentation, journal fit, benchmark scoring, provenance, and warnings in XLSX/HTML.
   - Generate HTML as a self-contained report that shows Table 1, cohort flow, journal scope-fit recommendations, domain benchmark scores, blockers, and revision priorities.
   - Keep all formats numerically synchronized; do not separately reconstruct Table 1 values for each format.

15. Match journals against the supplied JCR reference set.
   - Load `references/jcr-journal-benchmark.md` and `references/jcr-2026-medicine-top69.csv`.
   - Treat the catalog as 69 journal-category records and 68 unique titles; preserve cross-category evidence and deduplicate recommendation display by title.
   - Label the metric as 2025 impact factor within the user-supplied JCR 2026 reference set.
   - Score scope/readership fit separately from the 10-point methodological benchmark. Neither score is an acceptance probability.

## Bundled Resources

- `references/equator-study-type-map.md`: study-type to reporting-guideline map and Table 1 implications.
- `references/study-intent-triage.md`: one-question-at-a-time intake contract, intent-to-design edges, confirmation gate, and LLM quality-improvement example.
- `references/design-method-matrix.md`: design-specific Table 1, enrollment flow, bias-control, validation, and method exclusions.
- `references/table1-statistical-decisions.md`: statistics, tests, denominators, SMD, weighting, missingness, and package guidance.
- `references/journal-style-profiles.md`: journal-family Table 1 conventions and caption/footnote preferences.
- `references/classic-layouts.md`: classic Table 1 shells for RCTs, observational/RWE studies, cohorts, case-control studies, diagnostic/prognostic studies, AI/model studies, and protocols.
- `references/flowchart-design.md`: CONSORT, STROBE/RECORD, STARD/Radiology, TRIPOD+AI, and protocol flowchart logic.
- `references/causal-design-matching.md`: DAG-based covariate selection, PSM/weighting/matching algorithms, transparency requirements, and bias warnings.
- `references/sensitivity-analyses.md`: multiple imputation, complete-case comparisons, E-values, model robustness, diagnostic/radiology sensitivity checks, and prediction-model validation.
- `references/design-specific-playbooks.md`: RWE, diagnostic accuracy, prediction/survival, medical AI, and RCT branch playbooks that connect Table 1, flowchart, grouping, and sensitivity analyses.
- `references/ai-healthcare-icaml.md`: ICAML-style AI healthcare study design guidance for quality improvement, workflow optimization, triage, CDSS, AI-assisted diagnosis, adoption, safety, and implementation evaluation.
- `references/benchmark-scoring.md`: 10-point JCR Top-1 medicine benchmark rubric for scoring study design, enrollment/flowchart, Table 1, plans, and target-journal fit.
- `references/jcr-journal-benchmark.md`: provenance, matching rules, and interpretation contract for the supplied JCR 2026 journal reference set.
- `references/jcr-2026-medicine-top69.csv`: normalized 69-record journal/category catalog derived from the supplied workbook.
- `scripts/design_study.py`: generate either a Markdown memo or a synchronized CSV/XLSX/HTML/Markdown package.
- `scripts/generate_study_package.py`: compute Table 1 from patient-level CSV/XLSX data and render the multi-format package.
- `scripts/import_jcr_reference.py`: refresh the normalized journal catalog from a compatible JCR workbook.
- `scripts/classify_study.py`: explainable proposal classifier and one-question clarification state machine.

## Script Use

Use Markdown-only mode for a quick memo:

```bash
python scripts/design_study.py study_spec.json --out study_design.md
```

Start with interactive triage when the research type is not confirmed:

```bash
python scripts/classify_study.py proposal.json --format markdown
python scripts/design_study.py proposal.json --triage --out study-intake.md
```

Store answers under `answers`/`intake_answers`. The script asks one next question per run. After all mandatory fields are resolved, set `confirmed_design` to the recommended `design_id`; only then generate final artifacts.

Use package mode for real files:

```bash
python scripts/design_study.py study_spec.json \
  --out-dir outputs/study-name \
  --formats xlsx,csv,html,md
```

The input JSON can include `study_title`, `study_type`, `clinical_area`, `journal`, `population`, `data_file`, `data_sheet`, `group_column`, `weight_column`, `id_column`, `groups`, `variables`, `include_overall`, `include_p_values`, `include_smd`, `show_missing`, `flowchart`, `flow_counts`, `time_zero`, `analysis_stage`, `matching`, `matching_status`, `missing_data`, `imputation_status`, `sensitivity_analyses`, `benchmark`, `target_jcr_category`, `journal_catalog`, and `notes`.

Define each variable as `{"name": "source_column", "label": "Publication label", "type": "continuous|categorical", "summary": "mean_sd|median_iqr|n_percent", "unit": "optional", "levels": ["optional", "order"]}`. Resolve relative `data_file` and `journal_catalog` paths from the JSON specification directory.

Package requirements: Python with `pandas`, `numpy`, and `openpyxl`; `scipy` is optional and only used when p values are explicitly requested. For top-journal observational/RWE tables, default to `include_smd: true` and `include_p_values: false`.

For real-data observational packages, set `matching_status` to `completed` only after matching or weighting has actually been executed, and set `imputation_status` to `completed` only after MI estimates have been pooled or the displayed dataset is the intended imputed representation. Supply `flow_counts` with `source_population`, `potentially_eligible`, `eligible_at_time_zero`, `time_zero`, `exposure_assigned`, `baseline_sufficient`, `designed_cohort`, `primary_analysis`, and `sensitivity_analysis` where available. Missing execution status or attrition denominators must lower the automated benchmark and appear as blockers.

## Quality Gates

Before finalizing a Table 1, verify:

- The table population matches the manuscript Methods population and analytic denominator.
- The flowchart denominators reconcile with Table 1 denominators and every exclusion has a timing and reason.
- RWE time zero, exposure ascertainment, eligibility, lookback, and follow-up windows are explicit.
- Every variable has a unit, coding definition, and category ordering where relevant.
- Missingness handling is explicit and consistent.
- Baseline p values are not used as a proxy for randomization success or confounding control.
- SMDs are included for observational balance claims and interpreted descriptively.
- PSM/weighting models include true confounders and exclude intermediates, colliders, post-index variables, and post-outcome variables.
- Matching/weighting algorithms are reproducible and disclose discarded records, common support, caliper/ratio, replacement, and balance diagnostics.
- Missing-data methods include sensitivity comparisons when MI is used or when complete-case assumptions are fragile.
- Diagnosis/radiology designs identify one-gate versus two-gate sampling and address spectrum, verification, and reference-standard bias.
- Prediction-model designs report event counts, data split logic, Cox/time-to-event details when relevant, discrimination, calibration, C-index, and external validation.
- AI healthcare workflow studies state whether the primary question is implementation/workflow impact, clinical quality improvement, triage performance, diagnostic assistance, or predictive modeling; use ICAML-style workflow evaluation rather than TRIPOD/STARD/CONSORT by reflex.
- AI healthcare flowcharts reconcile eligible encounters, AI-triggered encounters, AI output, clinician review, action/override, safety exclusions, and final analyzed episodes.
- AI healthcare Table 1 includes patient/encounter characteristics, baseline workflow volume, clinician/site/context variables, AI exposure/adoption variables, and fairness-relevant strata.
- Weighted, matched, clustered, repeated-measures, or multi-site data are clearly footnoted.
- Footnotes define abbreviations, tests, transformations, weighting, matching, and denominator rules.
- The table can stand alone without requiring readers to reverse-engineer the Methods.
- The final scoring report states total score out of 10, subdomain scores, critical blockers, top-journal benchmark assumptions, and what specific changes would raise the score.
- CSV, XLSX, HTML, and Markdown values reconcile because they come from one computed Table 1 object.
- XLSX opens with separate `Table 1`, `Journal Fit`, `Benchmark`, and `Methods Notes` sheets and includes visible provenance and interpretation notes.
- HTML is self-contained, printable, and visibly separates journal scope fit from methodological benchmark scoring.
- Journal recommendations use the supplied JCR reference catalog, preserve cross-category evidence, and deduplicate journal titles in display.
- Continuous values use decimal half-up rounding at the displayed precision; do not rely on binary floating-point tie-to-even formatting for publication values.
- The benchmark distinguishes a declared matching/MI plan from an executed matching/weighting/imputation analysis and penalizes missing attrition-stage denominators.
- An unconfirmed proposal stops at triage and returns one next question instead of generating a false-precision study package.
- The final method bundle matches the confirmed design: PSM is not defaulted for RCT, ITS/CITS, diagnostic accuracy, prediction, qualitative, economic, or evidence-synthesis studies.
