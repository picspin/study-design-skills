# PDBC Study Design Skills

**Multi-agent biomedical study-design plugin** — triage, validate, render, report-compliance audit, Cochrane evidence benchmark. Supports **Claude Code**, **Codex**, **OpenCode**, **OpenClaw**, and **Hermes**.

---

## What it does

Route any biomedical research proposal through a deterministic 8-step pipeline:

| Step | What | Script |
|------|------|--------|
| 1 | **Triage** — clarify the study idea, confirm design | `classify_study.py` |
| 2 | **Route** — load design-specific references, rubrics | `route-registry.json` |
| 3 | **Author** — build versioned JSON specification | `compile_study_spec.py` |
| 4 | **Validate** — schema + density checks | `validate_study_spec.py` |
| 5 | **Render** — Table 1, flowchart, XLSX, HTML, Markdown | `generate_study_package.py` |
| 6 | **Score** — benchmark against JCR + design-specific rubrics | `select_rubrics.py` |
| 7 | **Compliance** — audit against EQUATOR reporting guideline | `check_reporting_compliance.py` |
| 8 | **Cochrane evidence** — lazy-load existing systematic-review effect estimates | `cochrane_evidence.py` |

### Covered study families

Randomized trials · ITS / CITS / DiD · Causal observational / RWE · Descriptive observational · Diagnostic accuracy · Comparative diagnostic accuracy · Prediction models (classic + AI/ML) · Systematic reviews / meta-analyses · Scoping reviews · Qualitative studies · Economic evaluations · AI healthcare workflows · Animal studies · Case reports

### Vendored checklists (27 files)

- **EQUATOR reporting guidelines:** CONSORT 2025, CONSORT-AI, STROBE, RECORD, STARD 2015, STARD-AI, TRIPOD 2015, TRIPOD+AI 2024, PRISMA 2020, PRISMA-DTA, SQUIRE 2.0, TREND, CHEERS 2022, SRQR, COREQ, ARRIVE 2.0, CARE, SPIRIT, CLAIM 2024, MI-CLEAR-LLM
- **Cochrane risk-of-bias tools:** RoB 2, ROBINS-I, ROB-ME, RoB NMA
- **Bristol/Cochrane bias tools:** QUADAS-3, QUADAS-C, PROBAST+AI

---

## Installation

### Claude Code (recommended)

```
/plugin marketplace add picspin/study-design-skills
/plugin install study-design-skills
```

### Cross-agent installer (Python)

```bash
git clone https://github.com/picspin/study-design-skills.git
cd study-design-skills
python3 installers/install.py --target all
python3 installers/install.py --self-test   # dry-run integrity check
```

### Bash installer

```bash
bash installers/install.sh
```

---

## Quick-start

```bash
# 1. Triage
echo '{"proposal": "Does Drug X reduce cardiovascular events in Type 2 diabetes?"}' > proposal.json
python3 skills/study-design-skills/scripts/classify_study.py proposal.json --format markdown

# 2. Build spec
python3 skills/study-design-skills/scripts/compile_study_spec.py proposal.json --out study-package.json

# 3. Validate
python3 skills/study-design-skills/scripts/validate_study_spec.py study-package.json

# 4. Render
python3 skills/study-design-skills/scripts/design_study.py study-package.json --out-dir outputs/my-study --formats xlsx,csv,html,md

# 5. Compliance check
python3 skills/study-design-skills/scripts/checklist_exists.py --guideline CONSORT
python3 skills/study-design-skills/scripts/check_reporting_compliance.py study-package.json manuscript.md --out qc/compliance.md

# 6. Cochrane evidence
python3 skills/study-design-skills/scripts/cochrane_evidence.py search "metformin type 2 diabetes cardiovascular"
```

---

## License

MIT. See [LICENSE](LICENSE).

## Citation

See `CITATION.cff`.