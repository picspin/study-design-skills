#!/usr/bin/env python3
"""Generate a self-contained, printable evaluation HTML page from pipeline outputs.

Reads a compiled study-package.json and optionally a compliance report and
Cochrane-evidence summary, then writes a standalone HTML assessment page suitable
for GitHub Pages deployment, manuscript-team review, or journal submission
support.

Usage
-----
  python scripts/generate_evaluation_html.py study-package.json [options]

Options
-------
  --compliance PATH   Compliance report (Markdown or JSON from check_reporting_compliance.py)
  --cochrane   PATH   Cochrane-evidence output JSON from cochrane_evidence.py
  --out        PATH   Output HTML path (default: <slug>-evaluation.html)
  --study-title TEXT  Override display title
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_slug(value: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return s[:max_len] or "study-evaluation"


def _compliance_from_md(report_path: Path) -> dict:
    """Parse a Markdown compliance report into a structured dict."""
    text = report_path.read_text(encoding="utf-8")
    out: dict = {
        "guideline": "",
        "present": 0, "partial": 0, "missing": 0, "na": 0,
        "total": 0, "compliance_pct": 0.0,
        "items": [],
    }
    m = re.search(r"\*\*Guideline:\*\*\s*(\S+)", text)
    if m:
        out["guideline"] = m.group(1)
    for key, label in [("present", "PRESENT"), ("partial", "PARTIAL"),
                       ("missing", "MISSING"), ("na", "N/A")]:
        m2 = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*(\d+)", text)
        if m2:
            out[key] = int(m2.group(1))
    m3 = re.search(r"\*\*Overall compliance:\*\*\s*(\d+)/(\d+)\s*\(([\d.]+)%\)", text)
    if m3:
        out["compliance_pct"] = float(m3.group(3))
    out["total"] = sum(out[k] for k in ("present", "partial", "missing", "na"))
    # Parse item table rows
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("| ") and "|" in line[2:]:
            cells = [c.strip() for c in line.split("|")]
            if len(cells) >= 6:
                num, desc, status, loc, notes = cells[1], cells[2], cells[3], cells[4], cells[5]
                if status in ("PRESENT", "PARTIAL", "MISSING", "N/A", "NI", "NOT_SCANNED"):
                    out["items"].append({
                        "number": num, "description": desc[:80],
                        "status": status, "location": loc, "notes": notes,
                    })
    return out


def _compliance_from_json(report_path: Path) -> dict:
    data = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "guideline": data.get("guideline", ""),
        "present": data.get("present", 0),
        "partial": data.get("partial", 0),
        "missing": data.get("missing", 0),
        "na": data.get("na", 0),
        "total": data.get("total", 0),
        "compliance_pct": data.get("compliance_pct", 0.0),
        "items": data.get("items", []),
    }


def _cochrane_to_dict(cochrane_path: Path) -> dict:
    data = json.loads(cochrane_path.read_text(encoding="utf-8"))
    return {
        "total_reviews": data.get("total", 0),
        "records": [
            {
                "title": r.get("title", ""),
                "doi": r.get("doi", ""),
                "study_count": r.get("study_count"),
                "url": r.get("url", ""),
            }
            for r in data.get("records", [])
        ],
    }


DESIGN_LABELS: dict[str, str] = {
    "randomized_controlled_trial": "Randomized controlled trial",
    "stepped_wedge_cluster_rct": "Stepped-wedge cluster RCT",
    "controlled_interrupted_time_series": "Controlled interrupted time series",
    "interrupted_time_series": "Interrupted time series",
    "difference_in_differences": "Difference-in-differences",
    "observational_causal": "Observational causal / comparative effectiveness",
    "descriptive_observational": "Descriptive observational",
    "diagnostic_accuracy": "Diagnostic accuracy study",
    "comparative_diagnostic_accuracy": "Comparative diagnostic accuracy",
    "prediction_model_development": "Prediction model development",
    "prediction_model_validation": "Prediction model validation",
    "systematic_review_meta_analysis": "Systematic review with meta-analysis",
    "systematic_review_narrative": "Systematic review with narrative synthesis",
    "scoping_review": "Scoping review",
    "qualitative_study": "Qualitative study",
    "economic_evaluation": "Health economic evaluation",
}

# ---------------------------------------------------------------------------
# HTML fragments used as building blocks (avoid backslash-in-fstring problems)
# ---------------------------------------------------------------------------

BP = '<span class="badge badge-pres">PRESENT</span>'
BM = '<span class="badge badge-miss">MISSING</span>'
BPART = '<span class="badge badge-part">PARTIAL</span>'
BNA = '<span class="badge badge-na">N/A</span>'
BNS = '<span class="badge badge-na">NOT SCANNED</span>'


def _badge_html(status: str) -> str:
    return {
        "PRESENT": BP,
        "MISSING": BM,
        "PARTIAL": BPART,
        "N/A": BNA,
        "NI": BNS,
        "NOT_SCANNED": BNS,
    }.get(status, BNA)


def _pct_color(pct: float) -> str:
    if pct >= 80:
        return "#0f766e"
    if pct >= 50:
        return "#d97706"
    return "#a83b24"


# ---------------------------------------------------------------------------
# HTML template — use plain str.format() so CSS braces are not confused
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Study Evaluation — {study_title_esc}</title>
<style>
:root {{--ink:#162b36;--teal:#0f766e;--paper:#f6f8f8;--line:#d8e0e4;--muted:#65747c;--warn:#a83b24;--amber:#d97706}}
* {{box-sizing:border-box}}
body {{margin:0;background:var(--paper);color:var(--ink);font:14px/1.55 Arial,sans-serif}}
header {{background:var(--ink);color:#fff;padding:32px max(24px,calc((100vw - 1180px)/2)) 26px;border-bottom:6px solid var(--teal)}}
header h1 {{font-size:28px;margin:0 0 6px;letter-spacing:-0.01em}}
header p {{margin:0;color:#cbd7db;font-size:13px}}
header .meta {{display:flex;gap:12px;margin-top:14px;flex-wrap:wrap}}
header .meta span {{background:rgba(255,255,255,0.1);padding:3px 10px;border-radius:4px;font-size:12px}}
main {{max-width:1180px;margin:0 auto;padding:24px 24px 60px}}
h2 {{font-size:20px;margin:32px 0 12px;border-bottom:2px solid var(--ink);padding-bottom:6px}}
h3 {{font-size:16px;margin:22px 0 10px}}
.meta {{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}
.panel {{background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px 16px}}
.panel.warning {{border-left:4px solid var(--warn);background:#fef6f5}}
.label {{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:0.03em}}
.big {{font-size:28px;font-weight:700;color:var(--teal);line-height:1.1}}
.table-wrap {{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:4px}}
table {{width:100%;border-collapse:collapse;font-size:13px}}
th {{background:var(--teal);color:#fff;text-align:left;padding:8px 10px;position:sticky;top:0;font-weight:600}}
td {{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td {{border-bottom:none}}
.badge {{display:inline-block;padding:2px 7px;border-radius:3px;font-size:11px;font-weight:700}}
.badge-pres {{background:#d1fae5;color:#065f46}}
.badge-part {{background:#fef3c7;color:#92400e}}
.badge-miss {{background:#fee2e2;color:#991b1b}}
.badge-na {{background:#f1f5f5;color:#65747c}}
.pipeline-table td:first-child {{font-weight:600}}
.fine {{color:var(--muted);font-size:12px}}
ul {{padding-left:20px}}
ul li {{margin-bottom:4px}}
a {{color:var(--teal)}}
@media print {{header {{padding:20px}} main {{padding:12px}} .table-wrap {{overflow:visible}}}}
</style>
</head><body>

<header>
<h1>{study_title_esc}</h1>
<p>Study design evaluation report — generated by PDBC Study Design Skills pipeline</p>
<div class="meta">
  <span>{design_label_esc}</span>
  <span>Family: {family_esc}</span>
  <span>{timestamp}</span>
</div>
</header>

<main>

<!-- Pipeline Status -->
<section id="pipeline">
<h2>Pipeline status</h2>
<div class="table-wrap"><table class="pipeline-table">
<thead><tr><th>Step</th><th>Script</th><th>Status</th></tr></thead>
<tbody>{pipeline_rows}</tbody>
</table></div>
</section>

<!-- Study Summary -->
<section id="summary">
<h2>Study summary</h2>
<div class="meta">
  <div class="panel"><div class="label">Design</div><strong>{design_label_esc}</strong></div>
  <div class="panel"><div class="label">Flow layout</div><strong>{flow_layout_esc}</strong></div>
  <div class="panel"><div class="label">Study type</div><strong>{study_type_esc}</strong></div>
  <div class="panel"><div class="label">Time zero</div><strong>{time_zero_esc}</strong></div>
  <div class="panel"><div class="label">Population</div><strong>{population_esc}</strong></div>
  <div class="panel"><div class="label">Comparator</div><strong>{comparator_esc}</strong></div>
</div>
</section>

<!-- Method Stack -->
<section id="methods">
<h2>Method stack</h2>
<div class="meta">
  <div class="panel"><strong>Reporting guidelines</strong><ul>{guideline_rows}</ul></div>
  <div class="panel"><strong>Bias / appraisal tools</strong><ul>{bias_rows}</ul></div>
  <div class="panel"><strong>Analysis / validation methods</strong><ul>{methods_rows}</ul></div>
</div>
</section>

<!-- Design Warnings -->
<section id="warnings">
<h2>Design warnings</h2>
<div class="panel warning"><ul>{warnings_rows}</ul></div>
</section>

<!-- Scoring & Benchmark -->
<section id="scoring">
<h2>Design scoring &amp; benchmark</h2>
<div class="meta">
  <div class="panel"><div class="label">Current score</div><div class="big">{total_score}/10</div></div>
  <div class="panel"><div class="label">Post-revision ceiling</div><div class="big">{ceiling}/10</div></div>
</div>
{score_table_html}
{blocker_html}
{strength_html}
{priority_html}
</section>

<!-- Sample Size -->
<section id="sample">
<h2>Sample size</h2>
{sample_html}
</section>

<!-- Compliance Report -->
{compliance_html}

<!-- Cochrane Evidence -->
{cochrane_html}

<!-- Enrollment / Participant Flow -->
<section id="flow">
<h2>Enrollment &amp; participant flow</h2>
<div class="panel"><strong>Flow diagram placeholder</strong>
<p class="fine">The enrollment/participant flow diagram is rendered by <code>generate_study_package.py</code> as a CSS-styled HTML figure. Run the full pipeline with flow-counts specified to include the flow diagram.</p>
</div>
</section>

<!-- Journal Fit -->
<section id="journals">
<h2>Journal scope fit</h2>
{journal_html}
</section>

<!-- Output Artifacts -->
<section id="outputs">
<h2>Generated artifacts</h2>
<div class="panel"><ul>{output_rows}</ul></div>
</section>

</main>
</body></html>"""


def build_html(
    study_pkg: dict,
    compliance: dict | None = None,
    cochrane: dict | None = None,
    title_override: str | None = None,
) -> str:
    """Build a self-contained evaluation HTML page."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    study_title = title_override or study_pkg.get("study_title", "Untitled study")
    design_id = study_pkg.get("confirmed_design", "unknown")
    design_label = DESIGN_LABELS.get(design_id, design_id.replace("_", " ").title())
    route = study_pkg.get("route", {})
    family = route.get("family", "")
    flow_layout = route.get("flow_layout", "")
    study_type = study_pkg.get("study_type", "")
    population = study_pkg.get("population", "")
    comparator = study_pkg.get("comparator", "")
    time_zero = study_pkg.get("time_zero", "")
    guideline_stack = study_pkg.get("guideline_stack", [])
    bias_tools = study_pkg.get("bias_tools", [])
    analysis_methods = study_pkg.get("analysis_methods", [])
    warnings = study_pkg.get("design_warnings", [])

    # -- Escaped values ----------------------------------------------------
    study_title_esc = html.escape(study_title)
    design_label_esc = html.escape(design_label)
    family_esc = html.escape(family)
    flow_layout_esc = html.escape(flow_layout)
    study_type_esc = html.escape(study_type)
    population_esc = html.escape(str(population))
    comparator_esc = html.escape(str(comparator))
    time_zero_esc = html.escape(str(time_zero))

    # -- Pipeline status ---------------------------------------------------
    steps = [
        ("1. Triage", "classify_study.py", bool(route.get("resolution"))),
        ("2. Route", "route-registry.json", bool(route.get("design_id"))),
        ("3. Author spec", "compile_study_spec.py", bool(study_pkg.get("schema_version"))),
        ("4. Validate", "validate_study_spec.py", bool(study_pkg.get("route"))),
        ("5. Render", "generate_study_package.py", bool(study_pkg.get("study_title"))),
        ("6. Score", "select_rubrics.py", bool(route.get("rubric"))),
        ("7. Compliance audit", "check_reporting_compliance.py", compliance is not None),
        ("8. Cochrane evidence", "cochrane_evidence.py", cochrane is not None),
    ]
    pipeline_rows = "\n".join(
        '<tr><td>{}</td><td><code>{}</code></td><td><span class="badge {}">{}</span></td></tr>'.format(
            step, script,
            "badge-pres" if ok else "badge-miss",
            "PASS" if ok else "SKIP",
        )
        for step, script, ok in steps
    )

    # -- Method stack ------------------------------------------------------
    def _li(items, fallback="Not specified"):
        if items:
            return "\n".join("<li>{}</li>".format(html.escape(str(i))) for i in items)
        return '<li class="fine">{}</li>'.format(fallback)

    guideline_rows = _li(guideline_stack)
    bias_rows = _li(bias_tools)
    methods_rows = _li(analysis_methods)
    warnings_rows = _li(warnings, "No automatic warnings.")

    # -- Scoring -----------------------------------------------------------
    scoring = study_pkg.get("scoring", {})
    total_score = scoring.get("total", "—")
    ceiling = scoring.get("ceiling", "—")
    blockers = scoring.get("blockers", [])
    strengths = scoring.get("strengths", [])
    priorities = scoring.get("priorities", [])
    score_domains = scoring.get("domains", [])

    if score_domains:
        score_table_html = (
            '<div class="table-wrap"><table><thead><tr><th>Domain</th><th>Score</th>'
            '<th>Maximum</th></tr></thead><tbody>\n'
            + "\n".join(
                '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                    html.escape(d.get("domain", "")),
                    d.get("score", ""),
                    d.get("maximum", ""),
                )
                for d in score_domains
            )
            + "\n</tbody></table></div>"
        )
    else:
        score_table_html = ""

    blocker_html = ""
    if blockers:
        items = "\n".join("<li>{}</li>".format(html.escape(b)) for b in blockers)
        blocker_html = '<div class="panel warning"><strong>Blockers</strong><ul>{}</ul></div>'.format(items)

    strength_html = ""
    if strengths:
        items = "\n".join("<li>{}</li>".format(html.escape(s)) for s in strengths)
        strength_html = '<div class="panel"><strong>Strengths</strong><ul>{}</ul></div>'.format(items)

    priority_html = ""
    if priorities:
        items = "\n".join("<li>{}</li>".format(html.escape(p)) for p in priorities)
        priority_html = '<div class="panel"><strong>Revision priorities</strong><ol>{}</ol></div>'.format(items)

    # -- Sample size -------------------------------------------------------
    sample = study_pkg.get("sample_size", {})
    if sample.get("status") == "estimated":
        sample_html = (
            '<div class="meta">'
            '<div class="panel"><div class="label">Analyzable</div>'
            '<div class="big">{}</div></div>'
            '<div class="panel"><div class="label">Recruitment target</div>'
            '<div class="big">{}</div></div>'
            '<div class="panel"><div class="label">Method</div>'
            '<div>{}</div></div></div>'
        ).format(
            html.escape(str(sample.get("analyzable_n", "—"))),
            html.escape(str(sample.get("recruited_n", "—"))),
            html.escape(str(sample.get("method", ""))),
        )
    else:
        sample_html = '<div class="panel warning"><strong>Sample size</strong><p class="fine">Not estimated in this package.</p></div>'

    # -- Compliance report -------------------------------------------------
    compliance_html = ""
    if compliance:
        guideline = compliance.get("guideline", "")
        pct = compliance.get("compliance_pct", 0.0)
        present_c = compliance.get("present", 0)
        partial_c = compliance.get("partial", 0)
        missing_c = compliance.get("missing", 0)
        na_c = compliance.get("na", 0)
        total_c = compliance.get("total", 0) or max(1, present_c + partial_c + missing_c + na_c)
        p_color = _pct_color(pct)

        items_table = ""
        if compliance.get("items"):
            items_table = (
                '<div class="table-wrap"><table><thead><tr><th>#</th><th>Item</th>'
                '<th>Status</th><th>Location</th><th>Notes</th></tr></thead><tbody>\n'
                + "\n".join(
                    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                        html.escape(i.get("number", "")),
                        html.escape(i.get("description", "")[:80]),
                        _badge_html(i["status"]),
                        html.escape(i.get("location", "")),
                        html.escape(i.get("notes", "")),
                    )
                    for i in compliance["items"]
                )
                + "\n</tbody></table></div>"
            )
        else:
            items_table = '<p class="fine">No detailed item data available.</p>'

        compliance_html = (
            '<section id="compliance">\n'
            '<h2>Reporting compliance &mdash; {}</h2>\n'
            '<div class="meta">\n'
            '  <div class="panel"><div class="label">Compliance</div>'
            '<div class="big" style="color:{}">{:.0f}%</div></div>\n'
            '  <div class="panel"><div class="label">PRESENT</div>'
            '<div class="big" style="color:#0f766e">{}</div></div>\n'
            '  <div class="panel"><div class="label">PARTIAL</div>'
            '<div class="big" style="color:#d97706">{}</div></div>\n'
            '  <div class="panel"><div class="label">MISSING</div>'
            '<div class="big" style="color:#a83b24">{}</div></div>\n'
            '  <div class="panel"><div class="label">N/A</div>'
            '<div class="big" style="color:#65747c">{}</div></div>\n'
            '</div>\n{}\n</section>'
        ).format(
            html.escape(guideline),
            p_color, pct,
            present_c, partial_c, missing_c, na_c,
            items_table,
        )
    else:
        compliance_html = (
            '<section id="compliance">\n'
            '<h2>Reporting compliance</h2>\n'
            '<div class="panel warning"><strong>Not assessed</strong>'
            '<p>Run <code>python scripts/check_reporting_compliance.py '
            'study-package.json manuscript.md</code> before generating the '
            'evaluation page to include a compliance audit.</p></div>\n'
            '</section>'
        )

    # -- Cochrane evidence -------------------------------------------------
    cochrane_html = ""
    if cochrane:
        records = cochrane.get("records", [])
        total_reviews = cochrane.get("total_reviews", len(records))
        if records:
            rows = "\n".join(
                "<tr><td>{}</td><td>{}</td><td>{}</td>"
                '<td><a href="{}" target="_blank">View</a></td></tr>'.format(
                    html.escape(r.get("title", "")[:100]),
                    html.escape(r.get("doi", "")),
                    r.get("study_count", "—"),
                    html.escape(r.get("url", "#")),
                )
                for r in records
            )
            cochrane_html = (
                '<section id="cochrane">\n'
                '<h2>Cochrane evidence benchmark</h2>\n'
                '<div class="meta"><div class="panel"><div class="label">'
                'Reviews found</div><div class="big">{}</div></div></div>\n'
                '<div class="table-wrap"><table><thead><tr><th>Review title</th>'
                '<th>DOI</th><th>Studies</th><th>Link</th></tr></thead><tbody>\n'
                '{}\n</tbody></table></div>\n</section>'
            ).format(total_reviews, rows)
        else:
            cochrane_html = (
                '<section id="cochrane">\n'
                '<h2>Cochrane evidence benchmark</h2>\n'
                '<p class="fine">No Cochrane reviews matched. '
                'Manual search is recommended.</p>\n</section>'
            )
    else:
        cochrane_html = (
            '<section id="cochrane">\n'
            '<h2>Cochrane evidence benchmark</h2>\n'
            '<div class="panel warning"><strong>Not retrieved</strong>'
            '<p>Run <code>python scripts/cochrane_evidence.py search '
            '"intervention" --out cochrane.json</code> to include evidence '
            'benchmarks.</p></div>\n</section>'
        )

    # -- Journal fit -------------------------------------------------------
    journals = study_pkg.get("recommended_journals", [])
    if journals:
        rows = "\n".join(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(j.get("journal", "")),
                html.escape(j.get("category", "")),
                j.get("impact_factor", j.get("impact_factor_2025", "")),
                j.get("fit_score", j.get("fit_score", "")),
                html.escape(j.get("rationale", "")),
            )
            for j in journals[:8]
        )
        journal_html = (
            '<div class="table-wrap"><table><thead><tr><th>Journal</th>'
            '<th>Category</th><th>IF</th><th>Fit /10</th>'
            '<th>Rationale</th></tr></thead><tbody>\n'
            + rows
            + '\n</tbody></table></div>'
        )
    else:
        journal_html = '<div class="panel warning"><p class="fine">No journal-fit data in this package.</p></div>'

    # -- Output artifacts --------------------------------------------------
    outputs = study_pkg.get("_outputs", study_pkg.get("generated_files", []))
    if outputs:
        output_rows = "\n".join("<li>{}</li>".format(html.escape(str(p))) for p in outputs)
    else:
        output_rows = '<li class="fine">No output files recorded in this package.</li>'

    # -- Assemble ----------------------------------------------------------
    return _HTML_TEMPLATE.format(
        study_title_esc=study_title_esc,
        design_label_esc=design_label_esc,
        family_esc=family_esc,
        flow_layout_esc=flow_layout_esc,
        study_type_esc=study_type_esc,
        population_esc=population_esc,
        comparator_esc=comparator_esc,
        time_zero_esc=time_zero_esc,
        timestamp=now,
        pipeline_rows=pipeline_rows,
        guideline_rows=guideline_rows,
        bias_rows=bias_rows,
        methods_rows=methods_rows,
        warnings_rows=warnings_rows,
        total_score=total_score,
        ceiling=ceiling,
        score_table_html=score_table_html,
        blocker_html=blocker_html,
        strength_html=strength_html,
        priority_html=priority_html,
        sample_html=sample_html,
        compliance_html=compliance_html,
        cochrane_html=cochrane_html,
        journal_html=journal_html,
        output_rows=output_rows,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate self-contained evaluation HTML from pipeline outputs"
    )
    parser.add_argument("study_package", type=Path, help="Compiled study-package.json")
    parser.add_argument("--compliance", type=Path, help="Compliance report (Markdown or JSON)")
    parser.add_argument("--cochrane", type=Path, help="Cochrane-evidence output JSON")
    parser.add_argument("--out", type=Path, help="Output HTML path (default: <slug>-evaluation.html)")
    parser.add_argument("--study-title", help="Override display title")
    args = parser.parse_args()

    try:
        pkg = json.loads(args.study_package.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: study-package load failed — {e}", file=sys.stderr)
        return 1

    compliance_data: dict | None = None
    if args.compliance:
        text = args.compliance.read_text(encoding="utf-8").strip()
        if text.startswith("{"):
            compliance_data = _compliance_from_json(args.compliance)
        else:
            compliance_data = _compliance_from_md(args.compliance)

    cochrane_data: dict | None = None
    if args.cochrane:
        try:
            cochrane_data = _cochrane_to_dict(args.cochrane)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"WARNING: Cochrane load failed — {e}", file=sys.stderr)

    html_content = build_html(pkg, compliance=compliance_data, cochrane=cochrane_data, title_override=args.study_title)

    slug = safe_slug(args.study_title or pkg.get("study_title", "study"))
    out_path = args.out or Path(f"{slug}-evaluation.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"Written: {out_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())