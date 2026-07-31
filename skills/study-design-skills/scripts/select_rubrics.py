#!/usr/bin/env python3
"""Select shared and design-family evaluation criteria for a study spec."""

import argparse
import csv
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compile_study_spec import compile_spec


PACKAGED_RUBRIC_DIR = SCRIPT_DIR.parent / "evals" / "rubrics"


def read_rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def select_rubrics(source):
    spec = compile_spec(source)
    route = spec["route"]
    files = ["shared.csv", route["rubric"]]
    rows = []
    for name in files:
        path = PACKAGED_RUBRIC_DIR / name
        if path.exists():
            for row in read_rows(path):
                row["rubric_file"] = name
                rows.append(row)
    return {"route": route, "rubric_files": files, "criteria": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = select_rubrics(json.loads(args.spec.read_text(encoding="utf-8")))
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
