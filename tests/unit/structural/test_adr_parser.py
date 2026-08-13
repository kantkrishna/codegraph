# tests/unit/structural/test_adr_parser.py

# Tests for US-5.2 AC1 (Path Heuristics) and AC2 (Status/Decision Extraction).

from etl.connectors.markdown.adr_parser import extract_decision, extract_status, is_adr


def test_is_adr_path() -> None:
    assert is_adr("docs/adr/001-init.md") is True
    assert is_adr("architecture/decisions/002-db.md") is True
    assert is_adr("docs/api/setup.md") is False


def test_extract_status() -> None:
    content = "## Context\nBlah\n## Status\nAccepted\n## Decision\nWe will use Neo4j."
    assert extract_status(content) == "Accepted"


def test_extract_status_flexible_heading() -> None:
    content = "### status:\nProposed\n"
    assert extract_status(content) == "Proposed"


def test_extract_decision() -> None:
    content = "## Status\nAccepted\n## Decision\nUse Neo4j for the knowledge graph.\n## Consequences\nNone."  # noqa: E501
    decision = extract_decision(content)

    # Satisfy MyPy Optional[str] bounds
    assert decision is not None
    assert "Use Neo4j for the knowledge graph." in decision
