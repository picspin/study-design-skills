#!/usr/bin/env python3
"""On-demand official-API clients for study-design evidence retrieval."""

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
POLICY_PATH = SCRIPT_DIR.parent / "references" / "external-evidence-policy.json"
USER_AGENT = "study-design-skills/1.0 (research design evidence retrieval)"
MAX_RECORDS = 20


class EvidenceAPIError(RuntimeError):
    """Sanitized external-provider error that never includes credentials."""


def load_policy(path=POLICY_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def activation_decision(explicit_request=False, classification_context_gap=False, allow_external_context=False):
    if explicit_request:
        return {"activate": True, "reason": "explicit_user_request"}
    if classification_context_gap and allow_external_context:
        return {"activate": True, "reason": "classification_context_gap"}
    return {"activate": False, "reason": "default_disabled"}


def _limit(value):
    return max(1, min(int(value), MAX_RECORDS))


def _credential(name, required=True):
    value = os.getenv(name, "").strip()
    if required and not value:
        raise EvidenceAPIError(f"Missing required environment variable: {name}")
    return value


def _springer_credential(product):
    product_name = {
        "meta": "NATURE_META_API_KEY",
        "open_access": "NATURE_OPENACCESS_API_KEY",
    }[product]
    value = _credential(product_name, required=False) or _credential("NATURE_API_KEY", required=False)
    if not value:
        raise EvidenceAPIError(f"Missing required environment variable: {product_name} or NATURE_API_KEY")
    return value


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _redact(value):
    text = str(value)
    for name in ["NATURE_API_KEY", "NATURE_META_API_KEY", "NATURE_OPENACCESS_API_KEY", "SCOPUS_API_KEY", "NCBI_API_KEY"]:
        secret = os.getenv(name, "").strip()
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def _request(url, *, params=None, headers=None, data=None, timeout=30):
    query = urllib.parse.urlencode(params or {}, doseq=True)
    target = f"{url}?{query}" if query else url
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(target, data=data, headers=request_headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        detail = error.read(500).decode("utf-8", errors="replace")
        raise EvidenceAPIError(f"Provider returned HTTP {error.code}: {_redact(detail)}") from None
    except urllib.error.URLError as error:
        raise EvidenceAPIError(f"Provider connection failed: {error.reason}") from None


def _request_json(url, **kwargs):
    status, headers, body = _request(url, **kwargs)
    try:
        return status, headers, json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise EvidenceAPIError("Provider returned an invalid JSON response") from None


def _result(provider, endpoint, query, records, total=None, limitations=None):
    return {
        "provider": provider,
        "query": query,
        "records": records,
        "total": total,
        "provenance": {
            "endpoint": endpoint,
            "retrieved_at": _timestamp(),
            "limitations": limitations or [],
        },
    }


def search_springer_meta(query, limit=5):
    endpoint = "https://api.springernature.com/meta/v2/json"
    _, _, payload = _request_json(endpoint, params={"q": query, "s": 1, "p": _limit(limit), "api_key": _springer_credential("meta")})
    result = (payload.get("result") or [{}])[0]
    return _result("springer_meta", endpoint, query, payload.get("records", []), result.get("total"))


def search_springer_open_access(query, limit=5):
    endpoint = "https://api.springernature.com/openaccess/json"
    _, _, payload = _request_json(endpoint, params={"q": query, "s": 1, "p": _limit(limit), "api_key": _springer_credential("open_access")})
    result = (payload.get("result") or [{}])[0]
    return _result("springer_open_access", endpoint, query, payload.get("records", []), result.get("total"))


def get_springer_open_access_jats(query, limit=1, max_chars=20000):
    endpoint = "https://api.springernature.com/openaccess/jats"
    status, _, body = _request(endpoint, params={"q": query, "s": 1, "p": _limit(limit), "api_key": _springer_credential("open_access")}, headers={"Accept": "application/xml"})
    text = body.decode("utf-8", errors="replace")
    max_chars = max(1000, min(int(max_chars), 50000))
    return {
        "provider": "springer_open_access",
        "query": query,
        "status": status,
        "jats_xml": text[:max_chars],
        "truncated": len(text) > max_chars,
        "provenance": {"endpoint": endpoint, "retrieved_at": _timestamp(), "limitations": ["OA content only", "response excerpt may be truncated"]},
    }


def search_scopus(query, limit=5):
    endpoint = "https://api.elsevier.com/content/search/scopus"
    headers = {"X-ELS-APIKey": _credential("SCOPUS_API_KEY"), "Accept": "application/json"}
    _, response_headers, payload = _request_json(endpoint, params={"query": query, "count": _limit(limit), "start": 0, "view": "STANDARD"}, headers=headers)
    search_results = payload.get("search-results") or {}
    limitations = ["Coverage and fields depend on API-key and institutional entitlements"]
    quota = response_headers.get("X-RateLimit-Remaining")
    result = _result("scopus", endpoint, query, search_results.get("entry", []), search_results.get("opensearch:totalResults"), limitations)
    if quota is not None:
        result["provenance"]["rate_limit_remaining"] = quota
    return result


def search_clinical_trials(query, limit=5):
    endpoint = "https://clinicaltrials.gov/api/v2/studies"
    _, _, payload = _request_json(endpoint, params={"query.term": query, "pageSize": _limit(limit), "countTotal": "true", "format": "json"})
    return _result("clinical_trials", endpoint, query, payload.get("studies", []), payload.get("totalCount"))


def search_pubmed(query, limit=5):
    endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": _limit(limit), "tool": "study-design-skills"}
    api_key = _credential("NCBI_API_KEY", required=False)
    if api_key:
        params["api_key"] = api_key
    _, _, payload = _request_json(endpoint, params=params)
    search = payload.get("esearchresult") or {}
    records = [{"pmid": pmid} for pmid in search.get("idlist", [])]
    return _result("pubmed", endpoint, query, records, search.get("count"))


def search_nih_reporter(query, limit=5):
    endpoint = "https://api.reporter.nih.gov/v2/projects/search"
    request_body = {
        "criteria": {"advanced_text_search": {"operator": "and", "search_field": "all", "search_text": query}},
        "offset": 0,
        "limit": _limit(limit),
    }
    data = json.dumps(request_body).encode("utf-8")
    _, _, payload = _request_json(endpoint, data=data, headers={"Content-Type": "application/json"})
    return _result("nih_reporter", endpoint, query, payload.get("results", []), payload.get("meta", {}).get("total"))


PROVIDER_FUNCTIONS = {
    "springer_meta": search_springer_meta,
    "springer_open_access": search_springer_open_access,
    "scopus": search_scopus,
    "clinical_trials": search_clinical_trials,
    "pubmed": search_pubmed,
    "nih_reporter": search_nih_reporter,
}


def main():
    parser = argparse.ArgumentParser(description="Run one explicitly requested evidence-provider search.")
    parser.add_argument("provider", choices=sorted(PROVIDER_FUNCTIONS))
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = PROVIDER_FUNCTIONS[args.provider](args.query, args.limit)
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
