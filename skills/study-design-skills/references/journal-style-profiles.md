# Journal-Style Profiles For Table 1

Use this reference when the user asks for a journal-specific or high-impact biomedical style.

For recommendations based on the user-supplied JCR workbook, also load `jcr-journal-benchmark.md` and query `jcr-2026-medicine-top69.csv`. Keep journal scope fit separate from methodological benchmark scoring.

## Universal High-Level Style

- Make the table dense, self-contained, and clinically interpretable.
- Put units in row labels rather than separate prose.
- Keep decimals consistent: usually 0 or 1 decimal for percentages, 1 decimal for means/medians unless clinical precision requires more.
- Avoid decorative typography. Journal tables are instruments, not posters.
- Use footnotes to define abbreviations, denominators, missingness, and statistical methods.

## Nature, Science, Cell Families

Style:

- Compact main-text tables; detailed baseline tables often move to extended data or supplement.
- Strong preference for concise row blocks and minimal redundant rows.
- May emphasize cohort/data-source structure, sample provenance, and experimental/clinical context.

Use:

- Overall cohort plus key groups, or a compact summary of cohorts/datasets.
- Development/validation/test cohort structure for AI and omics work.
- Footnotes that clarify data source, acquisition platform, and analytic set.

Avoid:

- Long clinical variables in the main text when a supplementary table is more suitable.
- P values by default unless central to a stated comparison.

## JAMA Family

Style:

- Clinically disciplined and transparent.
- Strong captions and footnotes.
- Clear analysis population and denominator.

Use:

- Baseline p values are often discouraged for RCTs and are usually not the right balance display in RWE; SMDs may be used for observational balance.
- Missingness should be explicit when relevant.
- Row order should follow demographics, socioeconomic/contextual variables, clinical characteristics, comorbidities, medications, baseline outcomes.

## Lancet Family

Style:

- Dense but readable clinical tables with careful denominators.
- Often uses table footnotes to specify analysis sets, tests, and definitions.

Use:

- RCT arm columns or cohort exposure groups.
- Baseline clinical severity and setting are important.
- For pragmatic or global studies, include region/site/country-level descriptors when relevant.
- Default to SMDs rather than baseline p values for RWE balance tables unless the target journal or SAP asks otherwise.

## NEJM

Style:

- Highly concise, clinically central, and conservative.
- Main Table 1 often prioritizes variables that establish clinical comparability and disease context.

Use:

- RCT groups with no baseline significance testing unless explicitly justified.
- Strong definitions for baseline disease severity and key prognostic factors.
- Avoid overly broad exploratory variable blocks.
- In observational comparative effectiveness tables, use transparent balance metrics and put detailed covariate/matching diagnostics in supplement when the main table must remain concise.

## Circulation

Style:

- Cardiovascular clinical and epidemiologic clarity.
- Risk factors, medications, comorbidities, procedural details, and hemodynamic/imaging measures often matter.

Use:

- Include established cardiovascular risk factors, baseline medications, disease severity, biomarker units, imaging parameters, and procedural context.
- Use SMDs for registry/RWE comparative effectiveness studies.

## Journal Of Clinical Oncology

Style:

- Oncology-specific disease biology and treatment-history clarity.

Use:

- Cancer type/stage, line of therapy, ECOG or Karnofsky status, biomarkers, prior treatments, metastatic sites, molecular alterations, baseline tumor burden, follow-up.
- Distinguish safety, intention-to-treat, evaluable, and biomarker cohorts.

## Radiology

Style:

- Imaging acquisition and participant/dataset provenance are often essential.

Use:

- Scanner/vendor/protocol, modality, reader/rater context, imaging indication, disease spectrum, reference standard, site, image/lesion/patient unit.
- For AI imaging studies, separate patient-level and image-level denominators where both appear.
- Flowcharts should make one-gate versus two-gate sampling, reference-standard availability, unreadable/indeterminate images, and reader exclusions visible.

## Caption And Footnote Templates

RCT caption:

`Table 1. Baseline Characteristics of the Randomized Participants.`

Observational/RWE caption:

`Table 1. Baseline Characteristics of the Study Population by [Exposure/Treatment] Group.`

Prediction/AI caption:

`Table 1. Characteristics of Participants in the Development, Validation, and Test Cohorts.`

Diagnostic caption:

`Table 1. Participant Characteristics by Reference-Standard Disease Status.`

Minimum footnote pattern:

`Data are shown as mean (SD), median (IQR), or No. (%) unless otherwise indicated. Percentages were calculated using [denominator rule]. [Missingness rule]. [SMD/test/weighting definitions if used].`
