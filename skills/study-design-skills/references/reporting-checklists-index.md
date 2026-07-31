# Reporting Checklists — Master Index

**Vendored in:** `references/checklists/`  
**Last updated:** 2026-07-31  
**License:** CC BY (original guideline publications) — individual headers specify instrument-specific terms.

---

## Design-Type → Guideline Mapping

| Study family | Primary guideline | AI/ML extension | Risk-of-bias tool(s) |
|---|---|---|---|
| Randomized trial (parallel, cluster, crossover) | [CONSORT 2025](checklists/CONSORT_2025.md) | [CONSORT-AI](checklists/CONSORT_AI.md) | [RoB 2](checklists/ROB_2.md) |
| Stepped-wedge cluster RCT | [CONSORT 2025](checklists/CONSORT_2025.md) | — | [RoB 2](checklists/ROB_2.md) |
| Non-randomized intervention (ITS, CITS, DiD) | [TREND](checklists/TREND.md) + [SQUIRE 2.0](checklists/SQUIRE_2.md) | — | [ROBINS-I](checklists/ROBINS_I.md) |
| Observational — causal/RWE | [STROBE](checklists/STROBE.md) | — | [ROBINS-I](checklists/ROBINS_I.md) |
| Observational — descriptive | [STROBE](checklists/STROBE.md) | — | NOS (not vendored) |
| Routinely-collected health data | [STROBE](checklists/STROBE.md) + [RECORD](checklists/RECORD.md) | — | [ROBINS-I](checklists/ROBINS_I.md) |
| Diagnostic accuracy (single test) | [STARD](checklists/STARD.md) | [STARD-AI](checklists/STARD_AI.md) | [QUADAS-3](checklists/QUADAS_3.md) |
| Comparative diagnostic accuracy | [STARD](checklists/STARD.md) | [STARD-AI](checklists/STARD_AI.md) | [QUADAS-3](checklists/QUADAS_3.md) + [QUADAS-C](checklists/QUADAS_C.md) |
| Prediction model development/update | [TRIPOD](checklists/TRIPOD.md) | [TRIPOD+AI](checklists/TRIPOD_AI.md) | [PROBAST+AI](checklists/PROBAST_AI.md) |
| Prediction model external validation | [TRIPOD](checklists/TRIPOD.md) | [TRIPOD+AI](checklists/TRIPOD_AI.md) | [PROBAST+AI](checklists/PROBAST_AI.md) |
| Systematic review / meta-analysis | [PRISMA 2020](checklists/PRISMA_2020.md) | — | ROBIS / AMSTAR 2 |
| DTA systematic review | [PRISMA 2020](checklists/PRISMA_2020.md) + [PRISMA-DTA](checklists/PRISMA_DTA.md) | — | [QUADAS-3](checklists/QUADAS_3.md) |
| Qualitative — interviews/FGs | [SRQR](checklists/SRQR.md) + [COREQ](checklists/COREQ.md) | — | CASP Qualitative |
| Economic / cost-effectiveness | [CHEERS](checklists/CHEERS.md) | — | — |
| AI in clinical imaging | [CLAIM 2024](checklists/CLAIM_2024.md) | — | [PROBAST+AI](checklists/PROBAST_AI.md) |
| LLM accuracy in healthcare | [MI-CLEAR-LLM](checklists/MI_CLEAR_LLM.md) + primary guideline | — | — |
| Quality improvement / implementation | [SQUIRE 2.0](checklists/SQUIRE_2.md) | — | — |
| Animal / preclinical | [ARRIVE 2.0](checklists/ARRIVE_2.md) | — | — |
| Case report | [CARE](checklists/CARE.md) | — | — |
| Trial protocol | [SPIRIT](checklists/SPIRIT.md) | SPIRIT-AI | — |
| Network meta-analysis | PRISMA NMA extension | — | [RoB NMA](checklists/ROB_NMA.md) |
| Meta-analysis with missing evidence | PRISMA 2020 | — | [ROB-ME](checklists/ROB_ME.md) |

---

## Checklist Selection Logic

1. **Read** `route-registry.json` for the confirmed route's `family`.
2. **Look up** `family` in the table above → get primary guideline and AI extension.
3. **Check** the `study-package.json` `content_policy` for AI/ML flags.
4. **Run** `scripts/checklist_exists.py --guideline <name>` — exit 0 means vendored copy exists.
5. **Load** the vendored file from `references/checklists/<file>.md`.
6. **Scan** the manuscript and produce a compliance report.

**Fail-fast:** If a guideline is routed but its checklist file is missing,
`checklist_exists.py` exits 1 (`MISSING_CHECKLIST_CONTRACT_VIOLATION`).
Never construct checklist items from memory without `--allow-from-memory`.

---

## Risk-of-Bias Tool Selection

| Study design | Primary RoB tool | When to use |
|---|---|---|
| RCT | RoB 2 | All randomised trials |
| Non-randomised intervention | ROBINS-I | ITS, CITS, DiD, cohort with intervention |
| Diagnostic accuracy (single) | QUADAS-3 | Any DTA study |
| Diagnostic accuracy (comparative) | QUADAS-3 + QUADAS-C | Two tests compared within same sample |
| Prediction model | PROBAST+AI | Development or external validation |
| Systematic review | ROBIS or AMSTAR 2 | Per review type |
| Network meta-analysis | RoB NMA | When NMA is performed |
| Missing evidence in MA | ROB-ME | When evidence is suspected missing |