# Sensitivity Analyses For Table 1, Flowchart, And Study Design

Use this reference when the study involves missing data, RWE causal claims, diagnostic accuracy, radiology, prediction modeling, survival outcomes, matching/weighting, or high-impact clinical journals.

## Missing Data And Multiple Imputation

Use multiple imputation when missing baseline covariates are material and a defensible missing-at-random assumption is plausible.

Plan:

- Describe missingness by variable and group in Table 1 or supplement.
- Specify imputation method, number of imputations, imputation model variables, transformations, interactions, and outcome/event inclusion when appropriate for congeniality.
- Preserve time ordering: do not impute or define baseline predictors using variables that occur after time zero unless the model is explicitly post-baseline.
- Compare complete-case or non-imputed analysis with MI analysis.
- Report whether effect direction, magnitude, confidence interval, and clinical interpretation change.
- Add a missing-not-at-random or delta-adjustment sensitivity analysis when missingness may depend on unobserved values.

Avoid:

- Silently excluding missing values from denominators.
- Treating missingness as random without describing why.
- Using missing-indicator methods as the primary default for continuous covariates without justification.

## RWE And Observational Causal Sensitivity Analyses

Core options:

- Complete-case versus MI analysis.
- Alternative matching/weighting algorithm.
- Alternative caliper or trimming threshold.
- Alternative confounder set based on DAG uncertainty.
- High-dimensional PS or ML PS as a robustness check when clinically credible.
- Negative control outcome or exposure when available.
- Lagged exposure window to reduce reverse causation or protopathic bias.
- Active-comparator or new-user design when possible.
- Competing risk model for survival outcomes when death or other events preclude the outcome.
- E-value for unmeasured confounding when the effect measure and audience make it appropriate.
- Quantitative bias analysis for misclassification, unmeasured confounding, or selection bias when assumptions can be stated.

Report:

- Which sensitivity analysis addresses which bias.
- Whether estimates are directionally consistent.
- Whether differences are clinically meaningful, not only statistically significant.

## Diagnostic Accuracy And Radiology Sensitivity Analyses

Core options:

- One-gate versus two-gate design implications and subgroup analysis by clinical setting.
- Spectrum sensitivity: disease severity, referral source, inpatient/outpatient status, prevalence, and alternative diagnoses.
- Verification sensitivity: complete reference-standard subset versus imputed/corrected verification subset if applicable.
- Reference-standard sensitivity: alternative adjudication, composite reference standard, or delayed confirmation.
- Reader sensitivity: individual readers, consensus reads, blinded versus adjudicated reads.
- Inter-rater reliability: Cohen kappa, weighted kappa, Fleiss kappa, ICC, or agreement proportion as appropriate.
- Device/site sensitivity: scanner vendor, field strength, imaging protocol, software version, site, acquisition date.
- Threshold sensitivity: prespecified threshold, ROC/AUC, calibration of threshold-dependent measures.

Table 1 link:

- Include the covariates needed to judge spectrum and device/site bias.
- Separate patient-level, lesion-level, image-level, and study-level denominators.

## Prediction Model And Survival Sensitivity Analyses

Core options:

- Internal validation: bootstrap, cross-validation, temporal split, geographic split, or site split.
- External validation whenever a target-use setting differs from development data.
- Survival outcomes: Cox model, penalized Cox, flexible survival model, competing risk model, landmark model, or time-dependent covariates when needed.
- Performance: C-index/time-dependent C-index, calibration slope/intercept, calibration plot, Brier score, decision-curve analysis.
- Repeated observations or clustered sites: clustered bootstrap, mixed effects, robust SE, or grouped splits.
- Missing predictor sensitivity: complete-case, MI, missingness indicators only when justified, and unavailable-predictor scenario.
- Fairness/generalizability: subgroup performance by sex, age, race/ethnicity, site, device, disease severity, and care setting.

Table 1 link:

- Report events and follow-up by development, validation, and test cohort.
- Report predictors and missingness, not only demographics.

## RCT Sensitivity Analyses

Core options:

- Intention-to-treat, modified ITT, per-protocol, and safety populations.
- Missing outcome assumptions: multiple imputation, tipping-point analysis, worst/best case, mixed models, or inverse probability weighting.
- Final clinical outcome and clinically meaningful estimand should dominate Table 1 and flowchart logic.
- CONSORT flowchart must explain randomized, allocated, lost to follow-up, discontinued, and analyzed participants by arm.

Table 1 link:

- Table 1 usually describes randomized baseline characteristics.
- Avoid baseline p values unless required by SAP or journal-specific instruction.
