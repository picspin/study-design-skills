#!/usr/bin/env python3
"""Normalize a user-supplied JCR workbook into the skill journal catalog."""

import argparse
from pathlib import Path

import pandas as pd


COLUMN_MAP = {
    "期刊名": "journal",
    "ISSN号": "issn",
    "eISSN号": "eissn",
    "Wos学科信息": "wos_category",
    "引用索引版本": "citation_index",
    "总引用": "total_citations",
    "2025影响因子": "impact_factor_2025",
    "分区": "quartile",
}


def normalize_catalog(source: Path) -> pd.DataFrame:
    frame = pd.read_excel(source)
    missing = [column for column in COLUMN_MAP if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required JCR columns: {', '.join(missing)}")
    frame = frame.rename(columns=COLUMN_MAP)[list(COLUMN_MAP.values())].copy()
    frame.insert(0, "source_rank", range(1, len(frame) + 1))
    frame["journal"] = frame["journal"].astype(str).str.strip()
    frame["wos_category"] = frame["wos_category"].astype(str).str.strip().str.upper()
    frame["source_year"] = 2026
    frame["metric_year"] = 2025
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="JCR .xlsx source")
    parser.add_argument("output", type=Path, help="Normalized .csv output")
    args = parser.parse_args()

    catalog = normalize_catalog(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    catalog.to_csv(args.output, index=False, encoding="utf-8")
    print(
        f"Wrote {len(catalog)} records and "
        f"{catalog['journal'].str.casefold().nunique()} unique journals to {args.output}"
    )


if __name__ == "__main__":
    main()
