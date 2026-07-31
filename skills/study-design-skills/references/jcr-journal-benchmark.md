# JCR 2026 Medicine Top-Journal Reference Set

Use this reference when selecting candidate journals or calibrating editorial fit.

## Source Contract

- Catalog: `jcr-2026-medicine-top69.csv`.
- Provenance: user-supplied `JCR-70.xlsx`.
- Coverage: 69 journal-category records and 68 unique journal titles.
- Duplicate logic: preserve cross-category records; deduplicate by journal title in recommendation outputs. `JACC: CardioOncology` appears in cardiovascular and oncology categories.
- Year label: treat the workbook as the user's JCR 2026 reference set. The metric column is explicitly `impact_factor_2025`.
- Scope: the user states review-only journals were removed. Do not silently remove additional titles; flag title-type concerns for manual confirmation.

## Matching Contract

Rank journals using these dimensions:

1. WoS category and clinical-area fit.
2. Study-design and readership fit, such as general clinical outcomes, oncology, cardiovascular, radiology, or medical informatics.
3. Explicit user target-journal preference.
4. Reporting and artifact fit: Table 1, flowchart, missingness, causal design, AI workflow, and supplementary strategy.
5. Impact factor only as a secondary prioritization signal inside this supplied reference set.

Never present the fit score as an acceptance probability. Never use impact factor as a substitute for design quality. Recheck current author instructions before submission.

## Benchmark Selection

- General observational or RWE study: calibrate against the general/internal medicine subset and the relevant specialty subset.
- Specialty observational study: use the specialty category's strongest clinically oriented journals, then cross-check against Lancet/NEJM/JAMA/BMJ/Annals-style transparency.
- AI healthcare implementation: prioritize medical informatics and clinically relevant specialty journals; distinguish workflow/implementation studies from model-development studies.
- Imaging/diagnostic AI: prioritize radiology and medical imaging, while applying STARD-AI or the correct implementation guideline according to the primary question.
- Translational or experimental work: use research/experimental medicine only when the study contains a genuine mechanistic or translational contribution.

## HTML Reporting

Show:

- Recommended journal title.
- WoS category.
- 2025 impact factor exactly as supplied.
- Scope-fit score out of 10.
- One-line fit rationale.
- A visible disclaimer that scope fit is not acceptance probability.
