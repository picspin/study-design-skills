# Table 1 Statistical Decisions

Use this reference before computing, specifying, or reviewing Table 1.

## Variable Typing

| Variable type | Preferred display | Notes |
| --- | --- | --- |
| Continuous, approximately symmetric | mean (SD) | Include units in row label. Avoid excess decimals. |
| Continuous, skewed | median (IQR) | Use median (range) when expected by a specialty or for small descriptive clinical series. |
| Ordinal | n (%) by level, or median (IQR) if scale behavior is defensible | Preserve clinically meaningful order. Do not hide important levels. |
| Binary | n (%) for clinically meaningful level | State which level is shown. Show both levels when ambiguity is likely. |
| Nominal multi-level | n (%) for each level | Collapse sparse levels only with a transparent rule. |
| Date/calendar period | n (%) by period or median year (IQR) | Needed in RWE and secular-trend studies. |
| Follow-up | median follow-up (IQR/range), person-time, or censoring summary | Match the survival analysis plan. |
| Laboratory values | mean (SD) or median (IQR) plus units | Add transformed scale if log-transformed in analysis. |

## Denominator Policy

Always define percentages:

- Non-missing denominator: common for descriptive baseline summaries.
- Full column denominator: useful when missingness is itself informative.
- Survey/weighted denominator: report weighted percentage and unweighted n where journal permits.
- Matched-set denominator: clarify whether counts are patients, encounters, pairs, clusters, lesions, images, or observations.

## Missing Data

Show missing n (%) when:

- Missingness exceeds a small trivial amount.
- Missingness differs between comparison groups.
- The variable is used in adjustment, matching, weighting, prediction modeling, or eligibility.
- The journal expects transparent reporting.

Do not silently drop missing values. State whether missing was excluded from denominators, shown as a category, imputed, or handled by complete-case analysis.

## P Values

Use baseline p values sparingly.

- Randomized trials: generally avoid baseline p values because randomization, not hypothesis testing of baseline covariates, supports exchangeability.
- Observational studies: p values can describe group differences but should not substitute for confounding assessment.
- Matched/weighted studies: SMD is usually more informative than p values for balance.
- NEJM, Lancet, JAMA, and similar high-impact clinical styles commonly expect Table 1 to support clinical interpretation and balance assessment without baseline significance testing; default to no p values unless required by SAP or journal template.
- Small categorical cells: use Fisher exact or exact alternatives if p values are required.
- Skewed continuous variables: use rank-based tests if p values are required.

## Standardized Mean Differences

Use SMDs for balance claims in observational and RWE studies.

- Report absolute SMD unless directional imbalance matters.
- For matched, weighted, or propensity-score analyses, show post-design SMDs and optionally pre-design SMDs.
- Avoid hard universal cutoffs as proof of no confounding. Values around 0.1 are commonly used as a practical flag, not a guarantee.
- For multi-level categorical variables, use an appropriate overall or pairwise SMD definition and footnote it.

## Weighting, Matching, Clustering, And Repeated Measures

Weighted data:

- Distinguish unweighted counts from weighted percentages or weighted means.
- Report effective sample size if relevant.
- Use survey-aware or design-weighted procedures when available.

Matched data:

- Preserve matched-pair or matched-set denominator in footnotes.
- Do not use independent-sample tests when paired comparison is required.

Clustered or multi-site data:

- Clarify whether columns summarize participants, clusters, centers, images, lesions, admissions, or encounters.
- Consider site/center distribution when site drives case mix.

Repeated measures:

- Use the unit of analysis from Methods.
- Avoid counting multiple observations per patient as independent baseline rows unless the table is explicitly encounter-level.

## Software Guidance

Python:

- Prefer `tableone.TableOne` when a pandas DataFrame is available and conventional summaries are sufficient.
- Useful options include columns, categorical, continuous, groupby, nonnormal, p values, SMDs, labels, and exports to text, Markdown-like tabulation, HTML, LaTeX, or CSV depending on environment.
- Use pandas plus scipy/statsmodels when custom weighting, complex survey design, exact tests, or bespoke output is needed.

R:

- Prefer `tableone::CreateTableOne` or `tableone::svyCreateTableOne` for medical baseline summaries with p values and SMDs, including survey-weighted data.
- Prefer `table1::table1` when polished HTML output, labels, units, and custom rendering are more important than built-in inference.
- Use `gtsummary`, `gt`, `flextable`, or `knitr::kable` for manuscript and supplement formatting when available.

Spreadsheets:

- Use spreadsheets for final styling or audit trails only after statistical summaries are locked.
- Keep a separate data dictionary and calculation log to avoid hidden manual edits.

## Minimum Footnotes

Include footnotes for:

- Abbreviations.
- Summary formats: mean (SD), median (IQR), n (%).
- Denominator rule and missingness handling.
- Tests or balance metrics if present.
- Weighting, matching, imputation, survey design, clustering, or repeated-measure handling.
- Transformations, category collapsing, and clinically non-obvious definitions.

## Flowchart Consistency Check

Before finalizing statistics:

- Reconcile source population, eligible population, analytic cohort, and Table 1 n.
- Confirm exclusions happen in the order reported in Methods.
- Confirm baseline variables are measured before time zero/index/randomization/prediction time.
- Confirm final denominator is not a hidden complete-case subset unless complete-case analysis is the prespecified primary analysis.
