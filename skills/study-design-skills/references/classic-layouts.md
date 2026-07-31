# Classic Table 1 Layouts

Use these shells as starting points. Adapt rows to the study question, data source, specialty, and journal style.

## RCT Baseline Table

| Characteristic | Intervention (n = ) | Control (n = ) | Overall (n = ) |
| --- | ---: | ---: | ---: |
| Age, mean (SD), y |  |  |  |
| Female sex, No. (%) |  |  |  |
| Race and ethnicity, No. (%) |  |  |  |
| Body mass index, mean (SD) |  |  |  |
| Disease duration, median (IQR), y |  |  |  |
| Baseline disease severity score, mean (SD) |  |  |  |
| Key comorbidity 1, No. (%) |  |  |  |
| Key comorbidity 2, No. (%) |  |  |  |
| Baseline primary outcome measure, mean (SD) |  |  |  |
| Stratification factor/site/region, No. (%) |  |  |  |

Footnote: avoid baseline p values unless required.

## Observational Or Real-World Evidence Table

| Characteristic before/at Time Zero | Exposure/Treatment A (n = ) | Exposure/Treatment B (n = ) | SMD |
| --- | ---: | ---: | ---: |
| Age, mean (SD), y |  |  |  |
| Sex, No. (%) |  |  |  |
| Race and ethnicity, No. (%) |  |  |  |
| Index date/calendar period, No. (%) |  |  |  |
| Calendar year/index period, No. (%) |  |  |  |
| Data source/site/region, No. (%) |  |  |  |
| Lookback duration, median (IQR), mo |  |  |  |
| Disease severity marker, median (IQR) |  |  |  |
| Comorbidities, No. (%) |  |  |  |
| Medication use before index, No. (%) |  |  |  |
| Healthcare utilization before index, median (IQR) |  |  |  |
| Missing key covariate, No. (%) |  |  |  |

For matched/weighted studies, consider panels: before weighting/matching and after weighting/matching.

Minimum RWE footnote: define time zero/index date, baseline lookback window, treatment assignment window, follow-up start, weighting/matching algorithm, whether summaries are weighted/matched, and whether missing covariates were imputed.

## RWE Attrition And Matching Summary Table

| Cohort Construction Step | Overall, No. | Treatment A, No. | Treatment B, No. | Comment/Bias Check |
| --- | ---: | ---: | ---: | --- |
| Source population |  |  |  | Database coverage |
| Eligible before time zero |  |  |  | Criteria applied before index |
| Assigned exposure/treatment |  |  |  | New-user/active comparator |
| Sufficient lookback |  |  |  | Baseline covariate window |
| Complete key variables |  |  |  | Use MI if complete-case attrition is material |
| In common support |  |  |  | Positivity/overlap |
| Matched/weighted analytic cohort |  |  |  | Algorithm and discarded records |
| Primary outcome analysis cohort |  |  |  | Follow-up/outcome availability |

## Cohort Study Table

| Characteristic at Cohort Entry | Overall (n = ) | Exposed (n = ) | Unexposed (n = ) | SMD |
| --- | ---: | ---: | ---: | ---: |
| Age, mean (SD), y |  |  |  |  |
| Sex, No. (%) |  |  |  |  |
| Baseline risk factor block |  |  |  |  |
| Baseline disease status |  |  |  |  |
| Follow-up, median (IQR), y |  |  |  |  |
| Person-years |  |  |  |  |

## Case-Control Table

| Characteristic | Cases (n = ) | Controls (n = ) | SMD or P value |
| --- | ---: | ---: | ---: |
| Matching variables |  |  |  |
| Age at reference date, mean (SD), y |  |  |  |
| Sex, No. (%) |  |  |  |
| Exposure ascertainment window |  |  |  |
| Key confounders |  |  |  |
| Missing exposure data, No. (%) |  |  |  |

Footnote matching ratio and whether summaries account for matched sets.

## Diagnostic Accuracy Table

| Characteristic | Disease Present by Reference Standard (n = ) | Disease Absent by Reference Standard (n = ) | Overall (n = ) |
| --- | ---: | ---: | ---: |
| Age, mean (SD), y |  |  |  |
| Sex, No. (%) |  |  |  |
| Clinical setting, No. (%) |  |  |  |
| One-gate suspected population, No. (%) |  |  |  |
| Two-gate case/control sampling source, No. (%) |  |  |  |
| Disease spectrum/severity, No. (%) |  |  |  |
| Alternative diagnoses among disease-absent participants, No. (%) |  |  |  |
| Index test timing, median (IQR), d |  |  |  |
| Reference standard timing, median (IQR), d |  |  |  |
| Scanner/vendor/protocol/site, No. (%) |  |  |  |
| Prior treatment, No. (%) |  |  |  |
| Uninterpretable index test, No. (%) |  |  |  |
| Missing reference standard, No. (%) |  |  |  |

Footnote whether disease status was defined by the reference standard and whether readers/test interpreters were blinded.

## Prediction Model Or Medical AI Table

| Characteristic | Development (n = ) | Internal Validation (n = ) | External Test (n = ) |
| --- | ---: | ---: | ---: |
| Participants/encounters/images, No. |  |  |  |
| Events/outcomes, No. (%) |  |  |  |
| Follow-up, median (IQR) |  |  |  |
| Censored before horizon, No. (%) |  |  |  |
| Age, mean (SD), y |  |  |  |
| Sex, No. (%) |  |  |  |
| Site/source, No. (%) |  |  |  |
| Calendar period, No. (%) |  |  |  |
| Device/scanner/platform, No. (%) |  |  |  |
| Candidate predictors/features with missingness |  |  |  |
| Fairness-relevant covariates, No. (%) |  |  |  |

Footnote unit of analysis, data split logic, leakage prevention, missing predictor handling, and whether repeated observations exist.

## AI Healthcare Workflow Or ICAML-Style Table

| Characteristic | Pre-AI/Usual Care (n = ) | AI-Exposed or AI-Live (n = ) | SMD or Difference |
| --- | ---: | ---: | ---: |
| Eligible encounters/tasks, No. |  |  |  |
| Patients, No. |  |  |  |
| Age, mean (SD), y |  |  |  |
| Sex, No. (%) |  |  |  |
| Race/ethnicity/language, No. (%) |  |  |  |
| Clinical acuity/severity, No. (%) |  |  |  |
| Site/department/shift, No. (%) |  |  |  |
| Baseline workflow volume, median (IQR) |  |  |  |
| Baseline turnaround/queue time, median (IQR) |  |  |  |
| AI input available, No. (%) |  |  |  |
| AI trigger criteria met, No. (%) |  |  |  |
| AI output shown to clinician, No. (%) |  |  |  |
| Recommendation accepted/modified/overridden, No. (%) |  |  |  |
| Outcome/safety adjudication complete, No. (%) |  |  |  |
| Fairness-relevant subgroup, No. (%) |  |  |  |

Footnote unit hierarchy, AI model version, threshold, workflow stage, clinician role, acceptance/override definitions, safety review, and whether analyses are intention-to-expose or accepted-only.

## Sensitivity Analysis Matrix

| Bias Or Fragility Concern | Primary Approach | Sensitivity Analysis | Expected Reporting |
| --- | --- | --- | --- |
| Missing baseline covariates | Multiple imputation | Complete-case/non-imputed comparison | Direction, magnitude, CI, clinical interpretation |
| Residual confounding | DAG-informed PS model | Alternative covariate set, E-value, negative control | Which bias each check targets |
| Matching dependence | Primary PSM/weighting algorithm | Alternative caliper, ratio, trimming, overlap weights | Balance and effect estimate comparison |
| Diagnostic spectrum bias | Primary suspected population | Severity/site/referral subgroup | Sensitivity/specificity by subgroup |
| Verification bias | Complete reference-standard analysis | Verification-corrected or complete-case comparison | Direction and plausibility |
| Prediction overfitting | Internal validation | Bootstrap/cross-validation/external validation | C-index, calibration, decision curve |

## Protocol Table Shell

| Planned Baseline Variable | Definition/Coding | Source | Time Point | Planned Summary |
| --- | --- | --- | --- | --- |
| Age | Years at index/randomization | EHR/CRF | Baseline | mean (SD) or median (IQR) |
| Sex | Categories as collected | EHR/CRF | Baseline | No. (%) |
| Disease severity | Instrument and range | CRF | Baseline | mean (SD) |
| Key comorbidity | Definition/code list | EHR/registry | Lookback period | No. (%) |
| Missingness | Variable-level missing | Derived | Baseline | No. (%) |
