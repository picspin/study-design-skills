#!/usr/bin/env python3
"""Lazy-load Cochrane Library evidence client.

Wraps the Cochrane Library REST API v2 (api.cochranelibrary.com/api/v2/)
to retrieve systematic-review metadata — effect estimates, study counts,
risk-of-bias summaries — WITHOUT requiring an API key for open metadata.

Follows the same activation contract as external_evidence.py:
  - explicit user request → activate
  - classification_context_gap + allow_external_context → activate
  - routine rendering / Table 1 / sample-size → DO NOT ACTIVATE
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPT_DIR.parent / ".cochrane_cache"

BASE_URL = "https://api.cochranelibrary.com/api/v2"
USER_AGENT = "study-design-skills/1.0 (Cochrane evidence lazy-load)"
MAX_RECORDS = 10


class CochraneAPIError(RuntimeError):
    """Wraps an upstream Cochrane API error."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _request_json(endpoint: str, params: dict | None = None) -> dict:
    """GET a Cochrane API endpoint and return parsed JSON."""
    url = endpoint
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
        url = f"{endpoint}?{qs}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read(500).decode("utf-8", errors="replace")
        raise CochraneAPIError(f"Cochrane API HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise CochraneAPIError(f"Cochrane API connection failed: {e.reason}") from None


def _maybe_load_cache(cache_key: str) -> dict | None:
    """Return cached JSON if fresh (< 24 h)."""
    if not CACHE_DIR.is_dir():
        return None
    path = CACHE_DIR / f"{cache_key}.json"
    if not path.is_file():
        return None
    age = datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    if age > 86400:  # 24 hours
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_cache(cache_key: str, data: dict) -> None:
    """Write JSON cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{cache_key}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def activation_decision(
    explicit_request: bool = False,
    classification_context_gap: bool = False,
    allow_external_context: bool = False,
) -> dict:
    """Return activation verdict — same contract as external_evidence.py."""
    if explicit_request:
        return {"activate": True, "reason": "explicit_user_request"}
    if classification_context_gap and allow_external_context:
        return {"activate": True, "reason": "classification_context_gap"}
    return {"activate": False, "reason": "default_disabled"}


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------


def search_reviews(
    query: str,
    limit: int = 5,
    use_cache: bool = True,
) -> dict:
    """Search Cochrane Database of Systematic Reviews.

    Returns review metadata: title, DOI, authors, date, study-count estimate.
    """
    cache_key = f"search_{re.sub(r'[^a-z0-9]+', '_', query.lower())[:80]}"
    if use_cache:
        cached = _maybe_load_cache(cache_key)
        if cached:
            return cached

    payload = _request_json(
        f"{BASE_URL}/reviews/search",
        params={"q": query, "limit": min(limit, MAX_RECORDS)},
    )

    result = {
        "provider": "cochrane_cdsr",
        "query": query,
        "total": payload.get("total", 0),
        "records": [],
        "provenance": {
            "endpoint": f"{BASE_URL}/reviews/search",
            "retrieved_at": _timestamp(),
            "cache_hit": False,
        },
    }

    reviews = payload.get("reviews", payload.get("results", []))
    for r in reviews[:limit]:
        record = {
            "title": r.get("title", ""),
            "doi": r.get("doi", ""),
            "authors": r.get("authors", []),
            "published_date": r.get("publishedDate", r.get("date", "")),
            "study_count": r.get("studyCount", r.get("numberOfStudies")),
            "summary": r.get("summary", "")[:500],
            "url": f"https://www.cochranelibrary.com/cdsr/doi/{r.get('doi', '')}/full",
        }
        result["records"].append(record)

    if use_cache:
        _save_cache(cache_key, result)
    return result


def get_review(doi: str, use_cache: bool = True) -> dict:
    """Get detailed metadata for a specific Cochrane review by DOI."""
    cache_key = f"review_{doi.replace('/', '_')}"
    if use_cache:
        cached = _maybe_load_cache(cache_key)
        if cached:
            return cached

    payload = _request_json(f"{BASE_URL}/reviews/{doi}")

    result = {
        "provider": "cochrane_cdsr",
        "doi": doi,
        "title": payload.get("title", ""),
        "authors": payload.get("authors", []),
        "published_date": payload.get("publishedDate", ""),
        "abstract": payload.get("abstract", "")[:2000],
        "study_count": payload.get("studyCount", payload.get("numberOfStudies")),
        "participant_count": payload.get("participantCount", payload.get("numberOfParticipants")),
        "risk_of_bias": {
            "low": payload.get("lowRiskOfBias", payload.get("lowRiskStudies")),
            "unclear": payload.get("unclearRiskOfBias"),
            "high": payload.get("highRiskOfBias"),
        },
        "mesh_terms": payload.get("meshTerms", []),
        "provenance": {
            "endpoint": f"{BASE_URL}/reviews/{doi}",
            "retrieved_at": _timestamp(),
            "cache_hit": False,
        },
    }

    if use_cache:
        _save_cache(cache_key, result)
    return result


def summarize_evidence(
    intervention: str,
    condition: str,
    design_hint: str = "",
    limit: int = 3,
) -> dict:
    """Build a structured evidence summary for a proposed study.

    Searches Cochrane reviews matching intervention + condition,
    returns effect estimates and review characteristics.
    """
    query = f"{intervention} {condition}"
    if design_hint:
        query += f" {design_hint}"

    search_result = search_reviews(query, limit=limit)
    reviews = []
    for r in search_result.get("records", []):
        if r.get("doi"):
            detail = get_review(r["doi"])
            reviews.append({
                "title": detail["title"],
                "doi": detail["doi"],
                "study_count": detail["study_count"],
                "participant_count": detail["participant_count"],
                "risk_of_bias": detail["risk_of_bias"],
                "abstract_snippet": detail.get("abstract", "")[:300],
            })

    return {
        "query": query,
        "total_found": search_result.get("total", 0),
        "reviews": reviews,
        "summary_statement": _generate_summary_statement(reviews),
        "provenance": search_result["provenance"],
    }


def _generate_summary_statement(reviews: list) -> str:
    """Generate a plain-text summary of what Cochrane evidence exists."""
    if not reviews:
        return "No Cochrane reviews found matching this query."
    total_studies = sum(r.get("study_count") or 0 for r in reviews if r.get("study_count"))
    total_participants = sum(r.get("participant_count") or 0 for r in reviews if r.get("participant_count"))
    lines = [
        f"Found {len(reviews)} Cochrane review(s) with approximately "
        f"{total_studies} studies and {total_participants} participants.",
    ]
    for r in reviews:
        lines.append(f"  • {r['title']}")
        if r.get("risk_of_bias"):
            rob = r["risk_of_bias"]
            parts = []
            if rob.get("low") is not None:
                parts.append(f"Low RoB: {rob['low']}")
            if rob.get("high") is not None:
                parts.append(f"High RoB: {rob['high']}")
            if parts:
                lines.append(f"    Risk of bias: {', '.join(parts)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cochrane Library evidence lazy-load client")
    sub = p.add_subparsers(dest="command", required=True)

    # search
    s = sub.add_parser("search", help="Search Cochrane reviews")
    s.add_argument("query", help="Search query (e.g., 'metformin diabetes RCT')")
    s.add_argument("--limit", type=int, default=5)
    s.add_argument("--no-cache", action="store_true", help="Bypass cache")

    # get
    g = sub.add_parser("get", help="Get detail for one review by DOI")
    g.add_argument("doi", help="Review DOI (e.g., 10.1002/14651858.CD012345)")
    g.add_argument("--no-cache", action="store_true")

    # summarize
    sm = sub.add_parser("summarize", help="Structured evidence summary for one intervention+condition pair")
    sm.add_argument("intervention", help="Intervention name")
    sm.add_argument("condition", help="Condition / population")
    sm.add_argument("--design-hint", default="", help="e.g., RCT, observational, diagnostic")
    sm.add_argument("--limit", type=int, default=3)
    sm.add_argument("--no-cache", action="store_true")

    # activation-test
    at = sub.add_parser("activation-test", help="Test the activation gate contract")
    at.add_argument("--explicit", action="store_true")
    at.add_argument("--context-gap", action="store_true")
    at.add_argument("--allow-external", action="store_true")

    # clear-cache
    cc = sub.add_parser("clear-cache", help="Delete the Cochrane cache directory")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "activation-test":
        verdict = activation_decision(
            explicit_request=args.explicit,
            classification_context_gap=args.context_gap,
            allow_external_context=args.allow_external,
        )
        print(json.dumps(verdict, indent=2))
        return 0 if verdict["activate"] else 0

    if args.command == "clear-cache":
        if CACHE_DIR.is_dir():
            for f in CACHE_DIR.iterdir():
                f.unlink()
            CACHE_DIR.rmdir()
            print(f"Cache cleared: {CACHE_DIR}")
        else:
            print("No cache directory found.")
        return 0

    use_cache = not getattr(args, "no_cache", False)

    try:
        if args.command == "search":
            result = search_reviews(args.query, args.limit, use_cache)
        elif args.command == "get":
            result = get_review(args.doi, use_cache)
        elif args.command == "summarize":
            result = summarize_evidence(
                args.intervention, args.condition,
                design_hint=args.design_hint, limit=args.limit,
            )
        else:
            parser.print_help()
            return 1
    except CochraneAPIError as e:
        print(f"Cochrane API error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())