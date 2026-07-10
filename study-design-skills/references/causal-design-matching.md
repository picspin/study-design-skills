# Causal Design, Grouping, Matching, And Propensity Scores

Use this reference for observational, RWE, cohort, registry, case-control, comparative effectiveness, and target-trial emulation studies.

## Time Zero First

Define time zero before any grouping or matching:

- Eligibility must be assessed at or before time zero.
- Exposure/treatment assignment must be anchored to time zero or a prespecified grace period.
- Covariates must be measured before time zero or in a prespecified baseline lookback window.
- Follow-up starts at time zero or after a prespecified lag.
- Outcomes must occur after time zero.

Never define baseline using variables measured after outcome occurrence.

## DAG-Based Covariate Selection

Use clinical prior knowledge and directed acyclic graphs to decide what enters the propensity score or adjustment model.

Include:

- Common causes of exposure and outcome.
- Strong outcome predictors that are plausibly related to exposure selection.
- Calendar time, site, care setting, disease severity, and healthcare-use variables when they affect treatment choice and outcome.
- Eligibility-driving baseline variables when imbalance may change interpretation.

Exclude:

- Intermediates or mediators between exposure and outcome.
- Colliders and variables caused by both exposure and unmeasured causes of outcome.
- Variables measured after time zero.
- Variables measured after treatment initiation when treatment can affect them.
- Outcome variables, post-outcome variables, or future healthcare utilization.
- Instrument-like variables that strongly predict exposure but have no plausible relation to outcome, unless a causal analyst intentionally uses them for a specific design.

When uncertain, label variables as confounder, precision variable, mediator, collider, instrument candidate, or post-index variable before selecting the final model.

## Matching And Weighting Options

Choose the algorithm by estimand and data structure.

| Method | Typical use | Key reporting requirements |
| --- | --- | --- |
| Exact matching | Small number of essential variables, such as sex, site, stage, calendar period | Exact variables, unmatched counts, strata counts |
| Nearest-neighbor PSM | Common comparative effectiveness setup | PS model, ratio, caliper, replacement, matching order, random seed |
| Caliper PSM | Reduce poor matches | Caliper scale, often logit PS; unmatched/discarded participants |
| Mahalanobis within PS caliper | Strong continuous baseline variables | Distance variables and caliper definition |
| Optimal matching | Improve global match quality | Optimization criterion and software |
| Full matching | Preserve more participants | Subclass construction and weights |
| IPTW | Estimate ATE or ATT depending on weights | Weight formula, stabilization, truncation, positivity |
| Overlap weighting | Emphasize clinical equipoise/common support | Weight formula and target population |
| Entropy balancing | Force covariate moments to match | Balance constraints and convergence |
| Coarsened exact matching | Transparent matching on coarsened clinically meaningful strata | Coarsening rules and strata loss |

## Transparency Checklist

Report:

- Causal estimand: ATE, ATT, ATC, overlap population, target-trial contrast, or descriptive balance only.
- Exposure groups and time zero.
- Baseline covariate window and code definitions.
- DAG rationale or clinical confounder rationale.
- Propensity model form, interactions, nonlinear terms, and whether ML was used.
- Matching algorithm, ratio, replacement, caliper, exact constraints, order, seed, and software.
- Number discarded before and after matching/weighting.
- Common-support plots or summaries when important.
- Balance diagnostics before and after matching/weighting.
- SMD table and Love plot expectations.
- Outcome model used after design, including robust/clustered variance when needed.

## Balance Diagnostics

- Use absolute SMD as the default balance metric.
- Treat SMD <0.1 as a common descriptive target, not a proof of no confounding.
- Evaluate variance ratios for continuous variables when important.
- Check higher-order terms or clinically important interactions if they drive treatment selection.
- Do not rely on p values for balance after matching or weighting.

## Table 1 Reporting Pattern

For high-impact RWE:

- Prefer Table 1 with pre-design and post-design balance, or a main post-design table plus supplementary pre-design balance.
- Display weighted or matched summaries consistent with the final estimand.
- Footnote unweighted n, weighted percentages, effective sample size, and discarded participants.
- Put the algorithm details in Methods and footnote enough for readers to identify the design.

## Common Failure Modes

- Immortal time bias from assigning exposure after patients must survive to receive it.
- Adjustment for mediators that removes part of the treatment effect.
- Adjustment for post-index severity values affected by treatment.
- Excluding patients with missing covariates only after exposure assignment without bias analysis.
- Using outcome-informed variable selection for propensity models.
- Treating SMD <0.1 as eliminating unmeasured confounding.
