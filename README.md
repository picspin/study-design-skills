# Study Design Skills

Biomedical study-design skill for producing synchronized Table 1, participant-flow, journal-fit, and methodological benchmark deliverables.

It supports observational and real-world evidence studies, RCTs, diagnostic accuracy and radiology studies, prediction and survival models, AI healthcare workflows, CDSS, triage, and other EQUATOR-aligned designs.

## Outputs

One study specification can generate:

- publication-oriented Excel workbook (`Table 1`, `Journal Fit`, `Benchmark`, and `Methods Notes` sheets);
- machine-readable CSV Table 1;
- self-contained HTML study-design report;
- Markdown design memo;
- design-specific flow and attrition logic;
- journal scope-fit recommendations and a 10-point methodological benchmark.

The observational/RWE workflow emphasizes time zero, DAG-informed confounder selection, transparent matching or weighting, SMD rather than baseline P values, missing-data handling, and sensitivity analyses. Planned PSM/MI is scored differently from completed matching, weighting, or imputation.

## Repository Layout

```text
study-design-skills/
  SKILL.md
  references/
  scripts/
examples/
  observational_package_spec.json
  observational_patients.csv
```

## Quick Start

Create a Python environment and install the runtime dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate an observational-study package:

```bash
python study-design-skills/scripts/design_study.py \
  examples/observational_package_spec.json \
  --out-dir outputs/observational-cohort \
  --formats xlsx,csv,html,md
```

Triage a broad proposal one question at a time:

```bash
python study-design-skills/scripts/classify_study.py \
  examples/llm_quality_proposal.json \
  --format markdown
```

After answering the intake fields and confirming the recommended design, generate a CITS package:

```bash
python study-design-skills/scripts/design_study.py \
  examples/llm_quality_confirmed_cits.json \
  --out-dir outputs/llm-quality-cits \
  --formats xlsx,csv,html,md
```

Generate a Markdown-only design memo:

```bash
python study-design-skills/scripts/design_study.py \
  examples/observational_package_spec.json \
  --out outputs/study-design.md
```

## Journal Reference Set

`references/jcr-2026-medicine-top69.csv` is normalized from a user-supplied workbook and contains 69 journal-category records representing 68 unique journal titles. The source set is labeled JCR 2026 and contains a 2025 impact-factor field.

Journal scope-fit scores are editorial aids, not acceptance probabilities. Impact factor is not used as a substitute for methodological quality. Confirm current author instructions and data-redistribution rights before making the repository public or redistributing the catalog.

## Important Boundaries

- The benchmark is an expert-style design and editorial-fit assessment, not a predicted acceptance rate.
- A declared matching, weighting, or MI plan is not treated as completed analysis.
- Reporting guidelines, risk-of-bias tools, and analysis methods are kept as separate layers.
- Prediction studies use internal/external validation rather than default PSM; ITS/CITS use repeated-time-series identification; comparative diagnostic accuracy uses QUADAS-C alongside QUADAS-3 for appraisal.
- Missing attrition denominators lower the benchmark and appear as blockers.
- The included example data are synthetic and contain no real patient information.

## 中文说明

该 skill 面向医学研究设计，可从同一份研究规格生成 Excel、CSV、HTML 和 Markdown，并统一输出 Table 1、入组流程、期刊匹配及 10 分制顶刊方法学评分。观察性研究默认关注 Time Zero、DAG 混杂变量、PSM/加权透明度、SMD、MI 与敏感性分析；仅写入统计计划但尚未真正执行时，不会获得“已完成分析”的评分。
