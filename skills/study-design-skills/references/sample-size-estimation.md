# Sample Size Estimation

Sample size belongs to the confirmed primary estimand, not merely to the broad study label. Do not calculate a final sample before the population, allocation/comparison structure, primary endpoint, effect or precision target, alpha, power/confidence width, clustering, and attrition or incomplete-pair mechanism are specified.

## Supported First-Pass Methods

- `parallel_proportions`: two independent event rates in a parallel RCT or comparative cohort. Required: `control_event_rate`, `intervention_event_rate`; optional: `alpha`, `power`, `allocation_ratio`, `loss_fraction`.
- `one_way_anova`: balanced omnibus comparison across independent groups. Required: `effect_size_f`; optional: `groups`, `alpha`, `power`, `loss_fraction`. Treat as a planning approximation for adjusted or robust models.
- `correlation`: two-sided correlation or partial-correlation planning using Fisher z. Required: `correlation`; optional: `alpha`, `power`, `variance_inflation_factor`, `loss_fraction`.
- `paired_binary`: directional discordant probabilities for a McNemar-style paired comparison. Required: `discordant_control_only` (`p01`) and `discordant_intervention_only` (`p10`); optional: `alpha`, `power`, `incomplete_pair_fraction`.
- `diagnostic_precision`: confidence-interval precision for sensitivity and specificity. Required: `sensitivity`, `specificity`, `prevalence`, `sensitivity_half_width`, `specificity_half_width`; optional: `alpha`, `uninterpretable_or_unverified_fraction`.
- `prevalence_precision`: single-proportion confidence-interval precision for cross-sectional surveys. Required: `half_width`; optional: `prevalence` (default 0.5), `alpha`, `design_effect`, `loss_fraction`, and a justified `population_size` for finite-population correction. This controls nominal sampling error, not volunteer, coverage, or nonresponse bias.
- `survival_events`: Schoenfeld event method. Required: `hazard_ratio`, `event_fraction`; optional: `alpha`, `power`, `intervention_fraction`, `loss_fraction`.

These are transparent planning estimates, not substitutes for final design-specific software, simulation, or biostatistical review. Use simulation for clustered, repeated-measure, adaptive, noninferiority, multireader-multicase, lesion-clustered, stepped-wedge, ITS, complex survival, multiplicity-adjusted, or prediction-model designs.

## Diagnostic Studies

State whether the primary target is sensitivity, specificity, AUC, paired difference, management impact, or reader performance. Precision-based sensitivity/specificity calculations do not automatically power a paired superiority comparison. Paired comparisons require directional discordance assumptions, not only total discordance. Inflate for uninterpretable tests, incomplete pairs, missing reference standards, clustering within patients, and reader/site effects where applicable.

## RCTs

Power the prespecified primary estimand and report analyzable and recruitment targets separately. Do not apply an arbitrary multicentre design effect to an individually randomized trial merely because centre is included in the model. Cluster randomization requires an ICC/design-effect or simulation-based adjustment.

## Reporting Contract

For a completed convenience survey, label any unrecorded planning assumptions as illustrative. Report the achieved sample and cluster-aware interval, not post-hoc power. Do not impute structurally inapplicable skip-pattern answers as ordinary missing data.

Every estimate must show method, formula, assumptions, analyzable sample, inflated recruitment target, unit, caveats, and provenance for the assumed effect. When assumptions are missing, return an explicit blocker instead of fabricating a number.
