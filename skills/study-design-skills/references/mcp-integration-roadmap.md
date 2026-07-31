# Medical Research MCP Integration Roadmap

Treat MCP as an evidence-retrieval layer, not as a substitute for study-design reasoning. Keep retrieved records, tool versions, timestamps, and source URLs in provenance.

## Activation Gate

All providers are disabled by default. Load `external-evidence-policy.json` and activate a provider only when:

1. the user explicitly requests an external search, precedent review, trial search, full-text retrieval, or funding landscape; or
2. classification cannot resolve an unfamiliar intervention, technology, endpoint, or intended use from local context and `allow_external_context` is explicitly true.

Do not activate external evidence for routine rendering, Table 1 construction, sample-size calculation, or benchmark scoring. An MCP tool call is itself explicit activation; an internal agent workflow must still record the activation reason.

## Tier 1: Stable Public APIs

### Springer Nature Meta And Open Access APIs

Documentation: `https://dev.springernature.com/docs/introduction/`

Use Meta v2 for versioned metadata and abstracts. Use the Open Access JSON endpoint for OA discovery and the OA JATS endpoint only when full-text methods or design details are needed.

MCP tools:

- `springer_meta_search(query, limit)`
- `springer_open_access_search(query, limit)`
- `springer_open_access_full_text(query, limit, max_chars)`

Read product-specific keys from `NATURE_META_API_KEY` and `NATURE_OPENACCESS_API_KEY`. `NATURE_API_KEY` remains a compatibility fallback, but one product's key may not be entitled to another product. Do not place keys in a study package. OA status does not by itself establish methodological quality, and JATS responses may require truncation before entering model context.

### Elsevier Scopus API

Documentation: `https://dev.elsevier.com/academic_research_scopus.html`

Use Scopus for abstract, citation, source, author, and affiliation metadata when PubMed or publisher-specific metadata is insufficient. Authenticate through the `X-ELS-APIKey` header using `SCOPUS_API_KEY`.

MCP tools:

- `scopus_search(query, limit)`

Availability and returned fields depend on the API key, institutional subscription, IP range, and entitlements. Scopus results are evidence-discovery metadata, not permission to retrieve or redistribute subscription full text.

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
- Keep credentials only in environment variables and redact provider errors.
- Bind the bundled HTTP MCP to `127.0.0.1` unless authenticated remote deployment is deliberately configured.

## Local HTTP MCP

Install optional dependencies and start the streamable HTTP endpoint:

```bash
pip install -r requirements-mcp.txt
export NATURE_OPENACCESS_API_KEY=...
export NATURE_META_API_KEY=...  # only when Meta API access is enabled
export SCOPUS_API_KEY=...
python study-design-skills/scripts/mcp_server.py
```

Default endpoint: `http://127.0.0.1:8765/mcp`.

The server exposes provider-specific tools rather than one automatic global search. This makes provider activation visible in the tool trace and keeps routine study-design generation offline.
