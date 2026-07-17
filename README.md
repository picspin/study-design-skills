# Study Design Skills

A production-oriented biomedical study-design skill that converts a proposal into one validated JSON content source, then renders synchronized Table 1, enrollment flow, sample-size, journal-fit, and benchmark artifacts.

The architecture borrows a useful pattern from Anthropic's K12 teacher skills: keep the main skill small and route-specific, keep content separate from rendering, load only the references required for the selected domain, and enforce readability with machine-checkable rules.

## Architecture

```text
proposal
  -> one-question triage
  -> confirmed design
  -> route-registry.json
  -> route-specific references
  -> canonical study-package JSON
  -> schema + method + density validation
  -> deterministic CSV/XLSX/HTML/Markdown renderers
  -> shared + design-family evaluation rubrics
```

The canonical JSON is the source of truth. HTML, XLSX, CSV, Markdown, and flowcharts are views of the same object, not separately authored documents.

```text
study-design-skills/
  SKILL.md
  schemas/
    study-package.schema.json
  references/
    route-registry.json
    external-evidence-policy.json
    clinical-language-density.md
    renderer-contract.md
    mcp-integration-roadmap.md
    ...
  evals/rubrics/
    shared.csv
    randomized-trial.csv
    causal-observational.csv
    diagnostic-accuracy.csv
    prediction.csv
    time-series-qi.csv
    ...
  scripts/
    classify_study.py
    compile_study_spec.py
    validate_study_spec.py
    select_rubrics.py
    external_evidence.py
    mcp_server.py
    design_study.py
    generate_study_package.py
examples/
tests/
```

## Design Routing

`references/route-registry.json` maps each confirmed design to:

- study-design family;
- required reference bundle;
- Table 1 profile;
- enrollment-flow layout;
- required content fields;
- methods that must not be applied by default;
- design-specific evaluation rubric.

Supported routes include randomized and stepped-wedge trials, ITS/CITS/DiD, causal and descriptive observational studies, diagnostic accuracy, prediction development and validation, evidence synthesis, qualitative studies, and economic evaluation.

The route keeps five layers separate: scientific question, study design, reporting guideline, bias tool, and analysis method. A familiar method such as PSM or multiple imputation cannot determine the design.

## JSON-Driven Workflow

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Triage an uncertain proposal:

```bash
python study-design-skills/scripts/classify_study.py \
  examples/llm_quality_proposal.json \
  --format markdown
```

Compile a confirmed or legacy flat specification:

```bash
python study-design-skills/scripts/compile_study_spec.py \
  examples/randomized_trial_confirmed.json \
  --out outputs/randomized-trial-study-package.json
```

Validate the contract and clinical-density rules:

```bash
python study-design-skills/scripts/validate_study_spec.py \
  outputs/randomized-trial-study-package.json

python study-design-skills/scripts/validate_study_spec.py \
  outputs/randomized-trial-study-package.json \
  --strict
```

Non-strict validation is appropriate while assumptions and approval-dependent data remain pending. Strict validation converts missing route-required content into errors.

Render synchronized outputs:

```bash
python study-design-skills/scripts/design_study.py \
  examples/randomized_trial_confirmed.json \
  --out-dir outputs/randomized-trial \
  --formats xlsx,csv,html,md
```

Each rendered package includes the exact compiled `*-study-package.json` used by the renderers and a manifest recording the route and schema version.

Select evaluation criteria:

```bash
python study-design-skills/scripts/select_rubrics.py \
  outputs/randomized-trial/randomized-trial-study-package.json \
  --out outputs/randomized-trial/selected-rubrics.json
```

## Output Contracts

- **Table 1:** randomized arms, exposure balance, diagnostic spectrum, periods/series, validation cohorts, participant context, or study characteristics according to the route.
- **Flowchart:** connected publication-style enrollment and analysis flow using the selected CONSORT, STARD, STROBE/RECORD, TRIPOD+AI, SQUIRE, or PRISMA-oriented layout.
- **Sample size:** assumptions and analyzable/recruited targets aligned to the primary estimand; unsupported complex designs return `assumptions_required`.
- **Benchmark:** shared criteria plus a design-family rubric and the JCR specialty profile, reported on a 10-point methodological/editorial-fit scale.
- **Language:** clinically readable blocks, compact flow nodes, short labels, structured comparison tables, and explicit separation of known, planned, pending, and not estimable.

The benchmark is not an acceptance probability. Planned matching, weighting, imputation, or validation is never scored as completed analysis.

## External Evidence And MCP

`references/external-evidence-policy.json` keeps every provider disabled by default. A provider is activated only by an explicit request, or by a classification context gap when external context has been allowed. Routine rendering, Table 1 generation, sample-size calculation, and scoring remain offline.

`references/mcp-integration-roadmap.md` defines three integration tiers:

1. official APIs for Springer Nature Meta/OA, Scopus, ClinicalTrials.gov, PubMed/NCBI E-utilities, and NIH RePORTER;
2. a curated, versioned local knowledge service for EQUATOR, Cochrane, and Bristol QUADAS materials;
3. deterministic statistical services for complex sample size, SMD/weighting diagnostics, DAG temporal checks, E-values, and risk-of-bias worksheets.

External retrieval must preserve source URL, version, retrieval date, and limitations. Patient-level data remain local; only de-identified search concepts may be sent to public services.

Start the optional local streamable HTTP MCP:

```bash
pip install -r requirements-mcp.txt
export NATURE_OPENACCESS_API_KEY=...
export NATURE_META_API_KEY=...  # optional, requires Meta API entitlement
export SCOPUS_API_KEY=...
python study-design-skills/scripts/mcp_server.py
```

The default endpoint is `http://127.0.0.1:8765/mcp`; `.mcp.json.example` contains the client entry. Credentials are read only from the MCP process environment; `.env` files and real keys are excluded from Git. `NATURE_API_KEY` remains a compatibility fallback for existing OA setups, but Springer Nature product entitlements can differ by key.

## Journal Reference Set

`references/jcr-2026-medicine-top69.csv` contains 69 category records representing 68 unique non-review journal titles from the supplied JCR workbook. Journal scope-fit is an editorial aid, not a substitute for methodological quality. Confirm current author instructions and data redistribution rights before public release.

## Development

Run the test suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The renderer migration is backward compatible. Legacy text inference remains only as a fallback; canonical `route.flow_layout` and `route.table_profile` take precedence, and new medical decision logic belongs in the route/compiler/reference layers.
