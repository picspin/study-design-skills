# Medical Research MCP Integration Roadmap

Treat MCP as an evidence-retrieval layer, not as a substitute for study-design reasoning. Keep retrieved records, tool versions, timestamps, and source URLs in provenance.

## Tier 1: Stable Public APIs

### ClinicalTrials.gov API v2

Base documentation: `https://clinicaltrials.gov/data-api`

Use for:

- finding registered studies with similar populations, interventions, comparators, outcomes, and designs;
- extracting enrollment targets, allocation, masking, eligibility, outcome timing, and status;
- benchmarking feasible sample sizes and common primary endpoints;
- checking whether a proposed study duplicates or differentiates from active trials.

MCP tools:

- `search_trials(query, filters, fields)`
- `get_trial(nct_id)`
- `compare_trial_designs(nct_ids)`
- `summarize_enrollment_and_endpoints(query)`

Do not treat registry entries as proof of efficacy or methodological quality.

### NCBI E-utilities / PubMed

Documentation: `https://www.ncbi.nlm.nih.gov/books/NBK25501/`

Use for:

- retrieving current reporting-guideline publications, design-method papers, validation studies, and comparable clinical studies;
- resolving PMID, DOI, journal, publication type, MeSH terms, and abstracts;
- building source-backed design rationales and journal precedents.

MCP tools:

- `search_pubmed(query, filters)`
- `fetch_pubmed_records(pmids)`
- `find_design_precedents(picos, design_family)`
- `find_guideline_publication(acronym)`

Respect NCBI rate limits and identify the application.

### NIH RePORTER API v2

Documentation: `https://api.reporter.nih.gov/`

Use for:

- identifying funded projects in the same clinical and methodological area;
- discovering active investigators, institutions, grant mechanisms, and project abstracts;
- assessing whether a proposal aligns with current NIH-funded priorities.

MCP tools:

- `search_funded_projects(text, institutes, years)`
- `get_project(project_number)`
- `summarize_funding_landscape(topic)`

Do not use funding history as a journal-quality or causal-validity score.

## Tier 2: Curated Local Knowledge Services

EQUATOR, Cochrane Methods, and Bristol QUADAS primarily publish human-readable web pages, downloadable documents, or papers rather than stable public JSON APIs for the full decision logic.

Build a versioned local knowledge service instead of scraping them live on every request:

1. Store only metadata, short original summaries, source URLs, versions, applicable study families, and update dates.
2. Link to authoritative checklist/tool files; do not redistribute restricted full text.
3. Require human review when a source version changes.
4. Expose provenance with every result.

Suggested MCP tools:

- `route_reporting_guideline(design_id, overlays)`
- `get_guideline_metadata(acronym, version)`
- `get_bias_tool_metadata(tool, version)`
- `list_required_design_domains(design_id)`
- `check_source_freshness(source_id)`

## Tier 3: Computation Services

Wrap deterministic statistical services only after the JSON contract is stable:

- sample-size simulation for ITS, cluster crossover, multireader diagnostic, survival, and prediction studies;
- SMD and weighting diagnostics;
- DAG validation and temporal-variable checks;
- E-value computation;
- QUADAS/RoB domain worksheet generation;
- ClinicalTrials.gov comparator extraction;
- PubMed precedent tables.

Return assumptions, formulas, software versions, seeds, warnings, and structured results. Never return only a number.

## Governance

- Pin source and tool versions.
- Cache API responses with retrieval timestamps.
- Keep PHI and patient-level files local; public MCP calls receive de-identified search concepts only.
- Separate evidence retrieval from normative design decisions.
- Log every external source used in the final package.
- Fail closed when a required source is unavailable: mark the relevant section `not verified`, not silently inferred.
