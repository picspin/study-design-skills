#!/usr/bin/env python3
"""Local, on-demand HTTP MCP facade for study-design evidence providers."""

import os

from mcp.server.fastmcp import FastMCP

from external_evidence import (
    activation_decision,
    get_springer_open_access_jats,
    load_policy,
    search_clinical_trials,
    search_nih_reporter,
    search_pubmed,
    search_scopus,
    search_springer_meta,
    search_springer_open_access,
)


HOST = os.getenv("STUDY_DESIGN_MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("STUDY_DESIGN_MCP_PORT", "8765"))
TRANSPORT = os.getenv("STUDY_DESIGN_MCP_TRANSPORT", "streamable-http")

mcp = FastMCP(
    "study-design-evidence",
    instructions="Call providers only after an explicit request or an allowed study-classification context gap. Never send PHI or patient-level data.",
    host=HOST,
    port=PORT,
    streamable_http_path="/mcp",
    stateless_http=False,
    json_response=True,
)


@mcp.tool()
def get_external_evidence_policy():
    """Return provider capabilities and the default-disabled activation policy."""
    return load_policy()


@mcp.tool()
def decide_external_evidence_activation(explicit_request: bool = False, classification_context_gap: bool = False, allow_external_context: bool = False):
    """Decide whether external evidence may be loaded for this workflow step."""
    return activation_decision(explicit_request, classification_context_gap, allow_external_context)


@mcp.tool()
def springer_meta_search(query: str, limit: int = 5):
    """Search Springer Nature versioned metadata and abstracts."""
    return search_springer_meta(query, limit)


@mcp.tool()
def springer_open_access_search(query: str, limit: int = 5):
    """Search Springer Nature open-access metadata."""
    return search_springer_open_access(query, limit)


@mcp.tool()
def springer_open_access_full_text(query: str, limit: int = 1, max_chars: int = 20000):
    """Retrieve an OA JATS XML excerpt for methods or design review."""
    return get_springer_open_access_jats(query, limit, max_chars)


@mcp.tool()
def scopus_search(query: str, limit: int = 5):
    """Search Scopus abstract, citation, affiliation, and source metadata."""
    return search_scopus(query, limit)


@mcp.tool()
def clinical_trials_search(query: str, limit: int = 5):
    """Search ClinicalTrials.gov study registrations for design precedents."""
    return search_clinical_trials(query, limit)


@mcp.tool()
def pubmed_search(query: str, limit: int = 5):
    """Search PubMed identifiers for guidelines, methods, and clinical precedents."""
    return search_pubmed(query, limit)


@mcp.tool()
def nih_reporter_search(query: str, limit: int = 5):
    """Search NIH RePORTER funded-project metadata."""
    return search_nih_reporter(query, limit)


if __name__ == "__main__":
    if TRANSPORT not in {"stdio", "sse", "streamable-http"}:
        raise SystemExit(f"Unsupported STUDY_DESIGN_MCP_TRANSPORT: {TRANSPORT}")
    try:
        mcp.run(transport=TRANSPORT)
    except KeyboardInterrupt:
        pass
