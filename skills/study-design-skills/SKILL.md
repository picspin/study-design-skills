---
name: study-design-skills
description: Use when a biomedical research idea must be clarified, classified, designed, validated, exported, reviewed, scored, or journal-targeted, including RCT, ITS/DiD, observational/RWE, diagnostic accuracy, prediction, evidence synthesis, qualitative, economic, and AI healthcare studies with Table 1, enrollment flow, sample size, bias control, and CSV/XLSX/HTML/Markdown outputs.
---

# Study Design Skills

Route a biomedical proposal to the correct study-design family, build one versioned JSON content source, validate it against design-specific requirements, and render synchronized study artifacts. Keep medical reasoning in the JSON and references. Keep layout and file formatting in deterministic scripts.

Act as a research methods coach and design reviewer for clinicians, medical students, nurses, technologists, statisticians, and research coordinators. Do not let PSM, multiple imputation, a regression model, or a familiar checklist determine the study design.

## Core Contract

Use this pipeline:

`proposal -> triage -> confirmed design -> route references -> study-package JSON -> validation -> renderers -> rubrics -> [optional: compliance audit] -> [optional: Cochrane evidence] -> [evaluation HTML]`

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
If a sufficiently specified scientific design is outside the registry, do not force it into a nearby clinical route. Identify the applicable reporting and bias-assessment statements, document the uncovered route, and extend the registry/reference bundle only after confirming the design with the user. The current registry is broad biomedical coverage, not a claim that every scientific design is precompiled.

The route determines:

- design family;
- flowchart layout;
- Table 1 profile;
- required content;
- forbidden defaults;
- reference bundle;
- design-specific rubric.

Load every file in `route.references` before authoring the study package. Do not load unrelated design references.

When TypeSafe/Jev is explicitly requested, load `references/typesafe-jev.md` and the installed `typesafe-ai` skill. Use Jev Choice as an advisory design judgment while keeping the user's confirmed design and the route registry authoritative. Use Jev Score as an auditable supplement to the final benchmark; it never replaces source reconciliation, statement-specific requirements, or privacy approval for an external call.

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
  --out-dir /Users/hilbert/Documents/PDBC/study-name \
  --formats xlsx,csv,html,md
```

The package must include:

- canonical `*-study-package.json`;
- CSV characteristics table;
- formatted XLSX workbook;
- self-contained printable HTML;
- Markdown memo;

For this PDBC installation, save every final package under `/Users/hilbert/Documents/PDBC/<study-name>/`. Scratch calculations may stay in the workspace. Never copy identifiable record-level source data into the final package.
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

## Optional — Step 7: Reporting Compliance Audit

After the study design is confirmed and rendered, you can audit the manuscript against the appropriate EQUATOR reporting guideline in one command:

```bash
python scripts/checklist_exists.py --guideline CONSORT   # fail-fast guard
python scripts/check_reporting_compliance.py study-package.json manuscript.md \
  --out qc/reporting-compliance.md --json
```

The pipeline **auto-selects** the guideline from the confirmed route:

| Route family | Primary guideline | AI extension | Bias tool |
|---|---|---|---|
| randomized_trial | CONSORT 2025 | CONSORT-AI | RoB 2 |
| time_series_qi | TREND + SQUIRE 2.0 | — | ROBINS-I |
| causal_observational | STROBE (+ RECORD) | — | ROBINS-I |
| descriptive_observational | STROBE | — | NOS |
| diagnostic_accuracy | STARD 2015 | STARD-AI | QUADAS-3 |
| comparative_diagnostic | STARD 2015 | STARD-AI | QUADAS-3 + QUADAS-C |
| prediction | TRIPOD 2015 | TRIPOD+AI 2024 | PROBAST+AI |
| evidence_synthesis | PRISMA 2020 | PRISMA-DTA | ROBIS / AMSTAR 2 |
| qualitative | SRQR + COREQ | — | CASP |
| economic | CHEERS 2022 | — | — |

**Fail-fast contract** — `checklist_exists.py` enforces that every guideline must have a vendored checklist file in `references/checklists/`. Never construct checklist items from model memory without the `--allow-from-memory` opt-in; a memory-based report must carry a `NON-AUTHORITATIVE` banner and must not be marked submission-ready.

**Registration-timing audit (Step 4c equivalent):** When a registration ID is present, verify:

1. The ID is present in Methods, Abstract, and cover letter.
2. The registration date precedes — or is explicitly disclosed as post-dating — data extraction.
3. Amendment dates are reported and consistent.
4. Cross-artifact agreement: registry record ↔ manuscript.
5. Retrospective-registration disclosure if indicated.

**PRISMA cascade arithmetic audit (Step 4d):** For systematic reviews, auto-verify the four flow equations:

```bash
python scripts/prisma_cascade_check.py \
  --identified 315 --duplicates 122 --screened 193 --screened-excluded 87 \
  --sought 106 --not-retrieved 12 --assessed 94 --assessed-excluded 42 \
  --included 52
```

Exit 0 = all equations hold; exit 1 = at least one arithmetic or cross-reference mismatch.

**Framework naming audit (Step 4e):** When an AI extension is used, verify the manuscript does not mix hyphenation, invent item labels, or reference "recent guidance" instead of naming the framework:

```bash
python scripts/check_framework_naming.py --manuscript manuscript.md --strict
```

**Output:** A compliance report (Markdown + optional JSON) with PRESENT/PARTIAL/MISSING per item, submission-ready checklist export, and priority-ordered action items.

## Optional — Step 8: Cochrane Evidence Lazy-Load (External Evidence)

**Available only when the user explicitly requests a Cochrane look-up, or when `allow_external_context` is true and the classification context is insufficient.** Never activate during routine rendering, Table 1 generation, or scoring.

Load `references/external-evidence-policy.json` before the first call.

The Cochrane Library REST API v2 (`api.cochranelibrary.com/api/v2/`) provides open-access review metadata. No API key is required for metadata searches (full text requires an institutional subscription).

### 8.1 Search for existing reviews

```bash
python scripts/cochrane_evidence.py search "metformin type 2 diabetes cardiovascular RCT" --limit 5
```

Returns: review titles, DOIs, study counts, participant counts, risk-of-bias summaries.

### 8.2 Get detailed review metadata

```bash
python scripts/cochrane_evidence.py get 10.1002/14651858.CD012345
```

Returns: abstract, study characteristics, RoB distribution (low/unclear/high).

### 8.3 Evidence summary for a proposed study

```bash
python scripts/cochrane_evidence.py summarize "metformin" "type 2 diabetes" --design-hint RCT
```

Generates a structured summary of the existing Cochrane evidence base relevant to the proposed intervention and population.

### 8.4 Which Cochrane risk-of-bias tool to use

After loading the applicable RoB checklist from `references/checklists/`:

| Study design | Cochrane RoB tool | # signalling questions |
|---|---|---|
| RCT (parallel, cluster, crossover) | RoB 2 | 14 across 5 domains |
| Non-randomised intervention | ROBINS-I | 26 across 7 domains |
| Non-randomised exposure | ROBINS-E | 25 across 7 domains |
| Network meta-analysis | RoB NMA | 8 across 4 domains |
| Missing evidence in meta-analysis | ROB-ME | 4 questions |

**Important:** Use the Cochrane tools alongside the QUADAS-3 / QUADAS-C / PROBAST+AI tools already vendored for diagnostic and prediction studies.

### 8.5 Lazy-load contract

```python
# In classification or design confirmation scripts:
decision = cochrane_evidence.activation_decision(
    explicit_request=False,
    classification_context_gap=True,
    allow_external_context=True
)
if decision["activate"]:
    result = cochrane_evidence.summarize_evidence(intervention, condition)
```

Record every external source used in the final package's `provenance` section. Mark unavailable evidence as `not verified`.

## External Evidence And MCP

**This section governs non-Cochrane external evidence providers (Springer Nature, Scopus, PubMed, NIH RePORTER, ClinicalTrials.gov).**

Load `references/mcp-integration-roadmap.md` when external tools are available or when building an MCP.

- External evidence is disabled by default. Load `references/external-evidence-policy.json` before activating a provider.
- Activate a provider only after an explicit user request, or for a classification context gap when `allow_external_context` is true.
- Prefer official APIs for Springer Nature Meta/OA, Scopus, ClinicalTrials.gov, PubMed/NCBI E-utilities, and NIH RePORTER.
- Treat EQUATOR, Cochrane, and Bristol QUADAS as curated, versioned knowledge sources unless a stable official API is documented.
- Record source, version, retrieval date, and limitations.
- Keep patient-level data local and send only de-identified search concepts to public services.
- Never invoke an external provider during routine rendering, Table 1 generation, or scoring.
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

## Pipeline Summary\n\n```\nproposal\n  │\n  ├─ Step 1: Triage (classify_study.py) ──── clarify & confirm design\n  │\n  ├─ Step 2: Route (route-registry.json) ─── select design, references, rubrics\n  │\n  ├─ Step 3: Author (compile_study_spec.py) ── build JSON content source\n  │\n  ├─ Step 4: Validate (validate_study_spec.py) ── schema + density checks\n  │\n  ├─ Step 5: Render (design_study.py) ───────── Table 1, flowchart, XLSX, HTML, MD\n  │\n  ├─ Step 6: Evaluate (select_rubrics.py) ───── benchmark scoring\n  │\n  ├─ [Optional] Step 7: Reporting compliance audit\n  │   checklists/ → check_reporting_compliance.py → PRESENT/PARTIAL/MISSING\n  │\n  └─ [Optional] Step 8: Cochrane evidence lazy-load\n      cochrane_evidence.py → effect estimates, review characteristics, RoB\n  \n  ┌─ Step 9: Evaluation HTML\n      generate_evaluation_html.py → standalone evaluation page\n      ├─ combines pipeline status, study summary, design scoring\n      ├─ reporting compliance PRESENT/PARTIAL/MISSING (when provided)\n      ├─ Cochrane evidence benchmark (when provided)\n      └─ journal scope fit and generated artifact inventory\n```\n\n## Bundled Resources

### References & Schemas (existing)
- `references/route-registry.json`: design routes, reference bundles, layouts, and rubrics.
- `schemas/study-package.schema.json`: versioned JSON contract.
- `references/study-intent-triage.md`: clarification and confirmation gate.
- `references/design-method-matrix.md`: design-specific artifact and method mapping.
- `references/clinical-language-density.md`: audience, readability, and structure constraints.
- `references/renderer-contract.md`: allowed renderer behavior and compatibility boundary.
- `references/mcp-integration-roadmap.md`: external evidence and MCP plan.
- `references/external-evidence-policy.json`: provider capabilities and activation gates.
- `references/flowchart-design.md`: flowchart contracts.
- `references/table1-statistical-decisions.md`: Table 1 computation and reporting.
- `references/causal-design-matching.md`: DAG and causal design.
- `references/sensitivity-analyses.md`: design-specific robustness.
- `references/sample-size-estimation.md`: sample-size contract.
- `references/journal-style-profiles.md`: journal-family presentation.
- `references/benchmark-scoring.md`: 10-point benchmark.
- `references/typesafe-jev.md`: optional Jev routing and conservative benchmark calibration.

### Reporting Checklists (NEW — 27 vendored files)
- `references/reporting-checklists-index.md`: master index with design→guideline mapping.
- `references/checklists/CONSORT_2025.md`, `CONSORT_AI.md`, `STROBE.md`, `RECORD.md`, `STARD.md`, `STARD_AI.md`, `TRIPOD.md`, `TRIPOD_AI.md`, `PRISMA_2020.md`, `PRISMA_DTA.md`, `SQUIRE_2.md`, `TREND.md`, `CHEERS.md`, `SRQR.md`, `COREQ.md`, `ARRIVE_2.md`, `CARE.md`, `SPIRIT.md`, `CLAIM_2024.md`, `MI_CLEAR_LLM.md`: EQUATOR/Nature/BMJ reporting guideline checklists — each with frontmatter (acronym, version, citation, license) and item tables.
- `references/checklists/ROB_2.md`, `ROBINS_I.md`, `ROB_ME.md`, `ROB_NMA.md`: Cochrane risk-of-bias tools — full signalling questions by domain.
- `references/checklists/QUADAS_3.md`, `QUADAS_C.md`, `PROBAST_AI.md`: Bristol/Cochrane bias tools for diagnostic accuracy and prediction models.

### Existing Scripts (10)
- `scripts/classify_study.py`: one-question triage.
- `scripts/external_evidence.py`: deterministic official-API clients.
- `scripts/mcp_server.py`: local on-demand HTTP MCP facade.
- `scripts/compile_study_spec.py`: canonical compiler.
- `scripts/validate_study_spec.py`: contract and density validator.
- `scripts/select_rubrics.py`: conditional rubric selector.
- `scripts/design_study.py`: orchestration entry point.
- `scripts/generate_study_package.py`: synchronized renderer and Table 1 computation.
- `scripts/sample_size.py`: sample-size calculation toolkit.
- `scripts/jev_review.py`: optional TypeSafe/Jev design and benchmark judgment adapter.
- `scripts/import_jcr_reference.py`: JCR benchmark import.

### Compliance, Evidence & Evaluation Scripts (6)
- `scripts/checklist_exists.py`: deterministic fail-fast checklist existence guard. Exit 0 = vendored, 1 = MISSING_CHECKLIST_CONTRACT_VIOLATION, 2 = UNKNOWN_GUIDELINE.
- `scripts/check_reporting_compliance.py`: auto-select guideline from design route, load vendored checklist, scan manuscript, produce PRESENT/PARTIAL/MISSING report.
- `scripts/cochrane_evidence.py`: Cochrane Library REST API v2 client. Lazy-load: search reviews, get review detail, build structured evidence summaries. Open-access metadata, no API key needed.
- `scripts/prisma_cascade_check.py`: PRISMA 2020 flow-diagram arithmetic auto-verify — four equations + two cross-references.
- `scripts/check_framework_naming.py`: AI extension naming audit — BASE_MISSING, HYPHEN_MIX, SELF_COINED_LABEL, VAGUE_GUIDANCE.
- `scripts/generate_evaluation_html.py`: standalone evaluation HTML page generator — reads study-package.json (plus optional compliance and Cochrane outputs) and produces a self-contained, printable report with pipeline status, study summary, design scoring, compliance table, Cochrane evidence, journal fit, and artifact inventory.

### Agent Plugin Manifests (NEW, project root)
- `.claude-plugin/marketplace.json`: plugin registration for Claude Code marketplace.
- `.plugin.json`: generic agent manifest (Codex, OpenClaw, Hermes).
- `plugin.yaml`: native OpenCode format.

### Installers (NEW)
- `installers/install.py`: cross-agent installer (Python) — targets claude, codex, opencode, openclaw, hermes, all. Also `--self-test` for integrity checks.
- `installers/install.sh`: bash installer equivalent.
