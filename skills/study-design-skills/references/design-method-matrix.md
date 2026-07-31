# Design-Specific Method Matrix

Use after the study-design triage has been confirmed. Select only methods that address the confirmed design's threats.

| Confirmed design | Table 1 / characteristics object | Enrollment or study flow | Primary bias control | Do not default to |
| --- | --- | --- | --- | --- |
| RCT / cluster RCT | Randomized arms; cluster context and stratification factors | CONSORT allocation, follow-up, analysis | Randomization, concealment, blinding, ITT, estimand | PSM; baseline P values |
| Stepped-wedge cluster RCT | Clusters/sequences, period, baseline outcome and case mix | Cluster rollout by randomized sequence | Period/cluster effects, ICC, contamination, transition handling | Treating rollout as ordinary pre/post |
| ITS | Population/context by period plus baseline level/slope and time-series descriptors | Repeated observations around prespecified intervention point | Segmented regression, autocorrelation, seasonality, co-interventions | PSM; one-pre/one-post comparison |
| Controlled ITS | Intervention and concurrent control series, baseline trends and composition | Parallel repeated series | Differential level/slope changes, autocorrelation, seasonality | Simple DiD with only two time points |
| DiD/event study | Intervention/control clusters before treatment, pre-trends, composition | Panel construction and rollout timing | Parallel-trends diagnostics, cluster inference, event-study leads/lags | Assuming balance from PSM alone |
| Observational causal/RWE | Exposure groups at time zero, confounders, severity, utilization; pre/post-design balance | Target-trial-aligned attrition | DAG, PS/weighting/g-methods, positivity, missingness, negative controls | Post-index covariates; outcome-driven exclusions |
| Descriptive/associational | Overall and prespecified strata | Sampling and measurement flow | Sampling, confounder-adjusted association, missingness | PSM without a causal estimand |
| Diagnostic accuracy | Spectrum by reference-standard status; patient/image/lesion levels | Index test and reference standard completion | One-gate sampling, blinding, verification, threshold handling | PSM as spectrum-bias correction |
| Comparative diagnostic accuracy | Shared spectrum and paired completeness | Common sample through tests A/B and reference standard | Fully paired/randomized comparison, order/reader control | Indirect comparison of unrelated samples |
| Prediction development | Development/internal/external validation cohorts; events and predictor missingness | Prediction time zero and dataset partitions | Bootstrap/resampling, shrinkage, calibration, external validation | PSM; random split as the only validation |
| External prediction validation | Intended-use population versus development context | Locked model through outcome ascertainment | Calibration, discrimination, utility, transportability | Refitting before reporting locked performance |
| Systematic review/meta-analysis | Study-characteristics table | PRISMA study selection | Design-specific RoB, heterogeneity, certainty | Patient-level baseline Table 1 |
| Qualitative | Participant/context characteristics | Recruitment and analytic sample | Reflexivity, sampling, credibility, audit trail | Inferential balance testing |
| Economic evaluation | Population, comparator, resources, costs, utilities, assumptions | Model/input flow | PSA, scenario and structural uncertainty | Clinical Table 1 as the only input summary |

## Diagnostic Appraisal

- Use QUADAS-3 as the current recommended QUADAS iteration for systematic reviews of diagnostic accuracy; it can also inform primary-study design.
- Use QUADAS-C for risk of bias in comparative accuracy questions and alongside QUADAS-3. It is not for indirect between-study comparisons and does not assess applicability by itself.

## Prediction Appraisal

- Use PROBAST+AI for prediction models using regression or AI methods.
- Use internal validation to estimate optimism and external temporal/geographic/site validation to assess transportability.
- Report discrimination, calibration, and clinical utility. A prediction study does not become less biased merely by matching cases and controls.

## Non-Randomized Intervention Appraisal

- Use ROBINS-I for effects of non-randomized interventions.
- For ITS/CITS, explicitly assess intervention independence from other changes, prespecified intervention timing, outcome-measurement changes, incomplete outcome data, and time-series model adequacy.

## Official Sources

- ROBINS-I: https://methods.cochrane.org/bias/risk-bias-non-randomized-studies-interventions
- Cochrane Prognosis tools and PROBAST+AI: https://methods.cochrane.org/prognosis/tools
- QUADAS-3: https://www.bristol.ac.uk/population-health-sciences/projects/quadas/
- QUADAS-C: https://www.bristol.ac.uk/population-health-sciences/projects/quadas/quadas-c/
