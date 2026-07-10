# JCR Top-1 Medicine Benchmark Scoring

Use this reference to score the generated study design package. Always state that the score is an expert-style methodological and editorial fit score, not a predicted acceptance probability.

## Benchmark Definition

Default benchmark:

- Load `jcr-journal-benchmark.md` and `jcr-2026-medicine-top69.csv` when the user requests journal matching or the supplied JCR 2026 benchmark.
- Use the supplied 69-record reference set to select a category-matched benchmark family. It contains 68 unique titles because one multidisciplinary title appears under two WoS categories.
- For general medicine, calibrate against the clinically oriented general/internal medicine subset rather than a single impact-factor rank.
- For specialty manuscripts, use category-matched clinically oriented journals, then cross-check against general top-tier transparency norms.

Important:

- Label the source accurately: user-supplied JCR 2026 reference set with a 2025 impact-factor field.
- Do not claim that the set is an official global rank or that a scope-fit score predicts acceptance.
- Do not use impact factor as a methodological-quality score.
- Use the benchmark to set methodological, reporting, transparency, clinical-impact, and presentation expectations.
- A score near 10 means the design package resembles a top-journal submission-ready methods artifact, not that the study will be accepted.

## Output Format

Always include:

1. Overall score: `x.x / 10`.
2. Benchmark used: journal family, JCR category, year if known, and why it was chosen.
3. Domain score table.
4. Critical blockers that cap the score.
5. Strengths that support top-journal fit.
6. Revision priorities ranked by expected score gain.
7. Post-revision ceiling estimate.

## Domain Rubric

| Domain | Max | What top score requires |
| --- | ---: | --- |
| Research question and design fit | 2.0 | Clinically important question, design matches causal/diagnostic/predictive/workflow aim, clear estimand, endpoint hierarchy, appropriate comparator. |
| Enrollment, time anchor, and flowchart | 1.5 | Transparent source population, eligibility, time zero/randomization/index-test/prediction/workflow anchor, attrition reasons, final denominators, and bias-aware flow. |
| Table 1 and baseline/context characterization | 1.5 | Variables reflect the design, disease severity, confounding structure, workflow/site context, missingness, units, denominators, SMD/weighting as appropriate, no inappropriate p values. |
| Statistical design and sensitivity analyses | 2.0 | Analysis plan matches estimand; DAG/PSM/weighting/MI/survival/diagnostic/prediction/AI workflow methods are transparent; sensitivity analyses map to specific biases. |
| Guideline compliance and reproducibility | 1.0 | Correct guideline family, transparent code/data/protocol/SAP/model version definitions, preregistration or protocol availability when expected. |
| Top-journal narrative and presentation fit | 1.0 | Concise, clinically interpretable, top-journal caption/footnotes, supplement strategy, no clutter, clear clinical implication and limitations boundary. |
| Safety, ethics, equity, and implementation realism | 1.0 | Patient safety, subgroup/fairness, generalizability, monitoring, governance, implementation feasibility, and harms are visible when relevant. |

Total: 10.0.

## Score Bands

| Score | Interpretation |
| ---: | --- |
| 9.0-10.0 | Top-journal-ready design artifact. Remaining issues are mostly polish, wording, or supplement organization. |
| 8.0-8.9 | Strong top-journal candidate package. One or two important design/reporting weaknesses remain. |
| 7.0-7.9 | Publishable design logic but below JCR Top-1 benchmark; likely needs stronger bias control, sensitivity analyses, or clearer endpoints. |
| 6.0-6.9 | Major methods or reporting gaps; credible for lower-impact venues only after revision. |
| 4.0-5.9 | Design and reporting mismatch. Flowchart, Table 1, endpoint, or analytic plan must be rebuilt. |
| <4.0 | Not yet scientifically defensible as a study design package. Requires redesign before journal targeting. |

## Critical Blockers

Apply a ceiling even if other areas look strong:

- No clear research question or primary endpoint: maximum 5.0.
- No valid time zero/index/randomization/prediction/workflow anchor: maximum 6.0.
- Flowchart denominator cannot reconcile with Table 1: maximum 6.5.
- RWE causal claim without confounding strategy: maximum 6.0.
- PSM/weighting includes intermediates, colliders, post-index variables, or outcome variables: maximum 5.5.
- Diagnostic study lacks reference-standard handling or one-gate/two-gate clarity: maximum 6.0.
- Prediction model lacks event counts, data split logic, calibration, and validation: maximum 6.5.
- AI healthcare workflow study reports only model performance and omits adoption, clinician action, safety, and fairness: maximum 6.5.
- Missingness is material but unreported or handled silently: maximum 7.0.
- Baseline p values are used as the main balance argument in RCT/RWE top-journal style: maximum 8.0.
- No sensitivity analysis for a design-sensitive observational, diagnostic, AI workflow, or survival study: maximum 7.0.

## Design-Specific Scoring Emphasis

### RWE And Observational Comparative Effectiveness

Require:

- Time zero and target-trial logic.
- DAG-driven confounder selection.
- No intermediate/post-outcome covariates in PS model.
- SMDs and transparent matching/weighting.
- MI versus complete-case sensitivity when missingness matters.
- E-value or quantitative bias analysis when causal claims are vulnerable.

### RCT

Require:

- CONSORT flow.
- Randomization and analysis populations.
- Clinically meaningful primary endpoint.
- No baseline p value dependence.
- Missing outcome and estimand strategy.
- Safety/harms visibility.

### Diagnostic Accuracy And Radiology

Require:

- One-gate versus two-gate design.
- Spectrum, verification, and reference-standard bias assessment.
- Patient/image/lesion/reader denominator clarity.
- Reference standard and blinding.
- Kappa or reader agreement when readers are involved.
- Device/site/protocol sensitivity when relevant.

### Prediction, Prognosis, And Survival

Require:

- Prediction time zero and outcome horizon.
- Event counts and follow-up.
- Development/validation/test split.
- Missing predictor handling.
- C-index or time-dependent C-index, calibration, and external validation when expected.
- Survival modeling aligned with censoring and competing risks.

### AI Healthcare, CDSS, Triage, And Workflow Optimization

Require:

- ICAML-style workflow framing when the primary question is implementation or human-AI workflow impact.
- Eligible encounter stream, AI trigger, output generation, clinician visibility, action/override, downstream outcome, safety ascertainment.
- Table 1 includes patient, encounter, workflow, clinician/site, AI exposure, adoption, and fairness variables.
- Endpoints include clinical quality, workflow, adoption, safety, and fairness.
- Sensitivity analyses include threshold, ramp-up, accepted-only versus intention-to-expose, secular trend, site/shift, model version, and subgroup/fairness checks.

## Scoring Report Template

```markdown
## JCR Top-1 Benchmark Scoring Report

Benchmark used: [General Medicine Top-1 / Specialty Top-1], target journal family: [Lancet/NEJM/JAMA/etc.], category/year: [if known].

Overall score: x.x / 10
Post-revision ceiling: y.y / 10

| Domain | Score | Rationale | Main fixes |
| --- | ---: | --- | --- |
| Research question and design fit | /2.0 |  |  |
| Enrollment, time anchor, and flowchart | /1.5 |  |  |
| Table 1 and baseline/context characterization | /1.5 |  |  |
| Statistical design and sensitivity analyses | /2.0 |  |  |
| Guideline compliance and reproducibility | /1.0 |  |  |
| Top-journal narrative and presentation fit | /1.0 |  |  |
| Safety, ethics, equity, and implementation realism | /1.0 |  |  |

Critical blockers:
- ...

Top strengths:
- ...

Revision priorities:
1. ...
2. ...
3. ...
```

## Calibration Notes

- Award 9+ only when the flowchart, Table 1, endpoint hierarchy, analytic plan, and sensitivity analyses are mutually consistent.
- Penalize attractive formatting if the scientific denominator logic is weak.
- Reward designs that explicitly state uncertainty, assumptions, and bias controls.
- Prefer concrete fix instructions over vague criticism.
