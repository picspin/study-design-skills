---
name: study-design-skills
description: Use when a biomedical research idea must be clarified, classified, designed, validated, exported, reviewed, scored, or journal-targeted, including RCT, ITS/DiD, observational/RWE, diagnostic accuracy, prediction, evidence synthesis, qualitative, economic, and AI healthcare studies with Table 1, enrollment flow, sample size, bias control, and CSV/XLSX/HTML/Markdown outputs.
---

# Study Design Skills

Route a biomedical proposal to the correct study-design family, build one versioned JSON content source, validate it against design-specific requirements, and render synchronized study artifacts. Keep medical reasoning in the JSON and references. Keep layout and file formatting in deterministic scripts.

Act as a research methods coach and design reviewer for clinicians, medical students, nurses, technologists, statisticians, and research coordinators. Do not let PSM, multiple imputation, a regression model, or a familiar checklist determine the study design.

## Core Contract

Use this pipeline:

`proposal -> triage -> confirmed design -> route references -> study-package JSON -> validation -> renderers -> rubrics`

Maintain one content source. Never separately rewrite Table 1, flowchart, HTML, XLSX, CSV, and Markdown content.

- Compile every confirmed input with `scripts/compile_study_spec.py`.
- Treat `schemas/study-package.schema.json` as the canonical contract.
- Render only from the compiled object.
- Save the compiled `*-study-package.json` with every package.
- Make revisions in the JSON source and rerender all formats.
- Do not put new clinical decision logic inside HTML/XLSX styling code.
- Load `references/renderer-contract.md` before changing a renderer.

## Route

### 1. Clarify only when needed

Load `references/study-intent-triage.md` for an idea, proposal, broad objective, or uncertain study label.

- Infer candidate designs and evidence.
- Ask exactly one unresolved question at a time.
- Prioritize scientific aim, allocation or rollout, concurrent comparator, data source, primary outcome family, and analysis unit.
- Narrow an overbroad proposal to one primary objective; retain other aims as secondary.
- Present the recommended design and closest alternative.
- Obtain explicit confirmation before generating final artifacts.
- Stop at the next question when the design is unconfirmed.

Use:

```bash
python scripts/classify_study.py proposal.json --format markdown
```

### 2. Resolve the design route

Load `references/route-registry.json`. Select the entry matching `confirmed_design`.

The route determines:

- design family;
- flowchart layout;
- Table 1 profile;
- required content;
- forbidden defaults;
- reference bundle;
- design-specific rubric.

Load every file in `route.references` before authoring the study package. Do not load unrelated design references.

Common routes:

| Family | Designs | Primary reference emphasis |
| --- | --- | --- |
| Randomized trial | Parallel, cluster, crossover, stepped wedge | CONSORT/SPIRIT, estimand, allocation, arm flow |
| Time-series/QI | ITS, CITS, DiD, rollout evaluation | SQUIRE, TREND, RECORD, repeated-time identification |
| Causal observational | RWE, target-trial, comparative effectiveness | STROBE/RECORD, time zero, DAG, weighting/matching |
| Descriptive observational | Cohort, case-control, cross-sectional | Sampling, measurement, association scope |
| Diagnostic accuracy | Single or comparative index tests | STARD, QUADAS-3/QUADAS-C, verification, spectrum |
| Prediction | Development, validation, updating, survival | TRIPOD+AI, PROBAST+AI, calibration, external validation |
| Evidence synthesis | Meta-analysis, narrative review, scoping review | PRISMA, design-specific risk of bias, synthesis fit |
| Qualitative | Interviews, focus groups, implementation mechanisms | SRQR/COREQ, reflexivity, information power |
| Economic | Cost-effectiveness and cost-utility | CHEERS, perspective, horizon, uncertainty |

Keep five layers separate:

1. scientific question;
2. study design;
3. reporting guideline;
4. bias/appraisal tool;
5. analysis method.

### 3. Author the JSON content source

Build or enrich one study specification. Include:

- `study_title`, `proposal`, `primary_objective`, `secondary_objectives`;
- `confirmed_design`, `population`, `setting`, `data_source`;
- `comparator`, `groups`, allocation unit, analysis unit;
- `time_zero`, lookback, follow-up, outcome horizon, or index/reference timing;
- primary estimand and endpoint hierarchy;
- Table 1 variables, summaries, denominators, missingness, SMD/p-value policy;
- flow counts and exclusion reasons;
- analysis methods, bias controls, sensitivity or validation plan;
- sample-size assumptions;
- journal target and benchmark inputs;
- provenance and unresolved assumptions.

Use `n = pending` for unknown protocol counts. Never invent data, sample sizes, guideline citations, or completed analyses.

Compile and validate:

```bash
python scripts/compile_study_spec.py input.json --out study-package.json
python scripts/validate_study_spec.py study-package.json
python scripts/validate_study_spec.py study-package.json --strict
```

Use non-strict validation during protocol development. Use strict validation before calling a package submission-ready.

## Design Rules

Apply only the methods appropriate to the confirmed route.

- RCT: randomization, concealment, blinding where feasible, estimand, intention-to-treat, missing outcomes, harms. Do not use PSM or baseline p values by default.
- ITS/CITS/DiD: repeated pre/post observations, intervention date, ramp-up, control series, pre-trends, autocorrelation, seasonality, co-interventions, composition, falsification checks. One pre and one post aggregate is not ITS.
- Causal observational/RWE: align eligibility, exposure, covariates, follow-up, and outcomes at time zero. Select confounders with clinical knowledge or a DAG. Exclude mediators, colliders, post-index, and post-outcome variables from propensity models.
- Descriptive observational: define the sampling frame, measurement timing, missingness, and association scope. Do not add PSM merely because groups exist.
- Diagnostic accuracy: state one-gate or two-gate sampling, index test, reference standard, timing, blinding, verification, thresholds, indeterminate results, readers, devices, and denominator units.
- Prediction: define prediction time, intended use, horizon, events/effective sample, missing data, shrinkage, bootstrap/resampling, calibration, discrimination, clinical utility, and independent validation. Do not use PSM as a generic correction.
- Evidence synthesis: use a study-characteristics table, not a patient baseline table. Match the risk-of-bias tool to included study designs.
- AI workflow/QI: distinguish model performance from clinical implementation. Track trigger, output generation, clinician visibility, acceptance/override, downstream action, adoption, safety, fairness, and secular trends.

Load `references/design-method-matrix.md` for the complete method mapping.

## Artifact Rules

### Table 1

- Match columns to randomized arms, exposure groups, diagnostic spectrum, periods/series, validation cohorts, or study characteristics.
- Preserve explicit denominator units.
- Prefer SMD over baseline p values for causal observational balance.
- Omit baseline p values in randomized trials by default.
- Put coding definitions and long variable descriptions in footnotes.
- Distinguish planned matching/imputation from executed analysis.

Load `references/table1-statistical-decisions.md` and `references/classic-layouts.md`.

### Enrollment and study flow

- Use a connected publication-style figure: cohort spine, side exclusions, branches, attrition, and final analysis sets.
- Reserve the PRISMA label for evidence synthesis; use CONSORT-, STARD-, STROBE/RECORD-, TRIPOD+AI-, ICAML/DECIDE-AI-, or SQUIRE-style labels elsewhere.
- Keep retained cohorts on the main path and exclusions on side paths.
- Reconcile every final denominator with Table 1.

Load `references/flowchart-design.md`.

### Sample size

- Derive sample size from the primary estimand.
- State effect or precision target, alpha/confidence width, power, allocation/pairing, clustering, incomplete observations, and inflation.
- Report analyzable sample and recruitment target separately.
- Require simulation for complex time-series, crossover cluster, multireader, lesion-level, adaptive, prediction, or repeated-measure designs when closed-form assumptions are insufficient.
- Emit an assumptions-required blocker instead of an invented number.

Load `references/sample-size-estimation.md`.

### Language and density

Load `references/clinical-language-density.md` for every route.

- Keep prose blocks to three sentences.
- Keep bullets to one clinical action or claim.
- Put parallel groups, periods, models, or study variants in one table.
- Put sequential enrollment, verification, allocation, dataset, or workflow information in a flowchart.
- Separate known, planned, pending approval, and not estimable.
- Remove generic claims of rigor, novelty, or comprehensiveness.

## Render

Generate synchronized files:

```bash
python scripts/design_study.py study-package.json \
  --out-dir outputs/study-name \
  --formats xlsx,csv,html,md
```

The package must include:

- canonical `*-study-package.json`;
- CSV characteristics table;
- formatted XLSX workbook;
- self-contained printable HTML;
- Markdown memo;
- manifest.

Use `scripts/generate_study_package.py` for patient-level CSV/XLSX computation. Keep calculation, rounding, denominators, and missingness synchronized across formats.

## Evaluate

Select shared and route-specific criteria:

```bash
python scripts/select_rubrics.py study-package.json --out selected-rubrics.json
```

Apply:

- `evals/rubrics/shared.csv`;
- the route-specific CSV named in `route.rubric`;
- `references/benchmark-scoring.md`;
- the applicable JCR specialty benchmark.

Judge each criterion independently. Report:

- pass/fail evidence by criterion;
- 10-point benchmark total and domain scores;
- critical blockers;
- highest-yield revisions;
- post-revision ceiling.

Do not describe the benchmark as publication probability.

## External Evidence And MCP

Load `references/mcp-integration-roadmap.md` when external tools are available or when building an MCP.

- Prefer official APIs for ClinicalTrials.gov, PubMed/NCBI E-utilities, and NIH RePORTER.
- Treat EQUATOR, Cochrane, and Bristol QUADAS as curated, versioned knowledge sources unless a stable official API is documented.
- Record source, version, retrieval date, and limitations.
- Keep patient-level data local and send only de-identified search concepts to public services.
- Mark unavailable external validation as `not verified`; do not silently infer it.

## Quality Gates

Before finalizing:

- confirm the route and design ID;
- validate required route content;
- reconcile flow and Table 1 denominators;
- verify time zero or the applicable clinical anchor;
- verify primary objective, estimand, endpoint, sample size, and model alignment;
- map each major bias to a control;
- verify missing-data and sensitivity logic;
- verify guideline and bias-tool versions;
- run clinical density checks;
- ensure all formats derive from the saved canonical JSON;
- distinguish pending plans from completed analysis;
- run tests and file QA.

## Bundled Resources

- `references/route-registry.json`: design routes, reference bundles, layouts, and rubrics.
- `schemas/study-package.schema.json`: versioned JSON contract.
- `references/study-intent-triage.md`: clarification and confirmation gate.
- `references/design-method-matrix.md`: design-specific artifact and method mapping.
- `references/clinical-language-density.md`: audience, readability, and structure constraints.
- `references/renderer-contract.md`: allowed renderer behavior and compatibility boundary.
- `references/mcp-integration-roadmap.md`: external evidence and MCP plan.
- `references/flowchart-design.md`: flowchart contracts.
- `references/table1-statistical-decisions.md`: Table 1 computation and reporting.
- `references/causal-design-matching.md`: DAG and causal design.
- `references/sensitivity-analyses.md`: design-specific robustness.
- `references/sample-size-estimation.md`: sample-size contract.
- `references/journal-style-profiles.md`: journal-family presentation.
- `references/benchmark-scoring.md`: 10-point benchmark.
- `evals/rubrics/`: shared and design-family criteria.
- `scripts/classify_study.py`: one-question triage.
- `scripts/compile_study_spec.py`: canonical compiler.
- `scripts/validate_study_spec.py`: contract and density validator.
- `scripts/select_rubrics.py`: conditional rubric selector.
- `scripts/design_study.py`: orchestration entry point.
- `scripts/generate_study_package.py`: synchronized renderer and Table 1 computation.
