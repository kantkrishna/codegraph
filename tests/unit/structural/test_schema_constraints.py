# tests/unit/structural/test_schema_constraints.py

# This file contains unit tests to verify the V1 and V2 Neo4j schema constraint definitions.

from scripts.apply_neo4j_constraints import get_schema_queries


def test_schema_queries_include_v1_and_v2_labels() -> None:
    """Test that all required V1 and V2 labels generate a UNIQUE constraint query."""
    queries = get_schema_queries()

    # V1 Labels
    assert any("Service" in q for q in queries)
    assert any("API" in q for q in queries)
    assert any("Database" in q for q in queries)
    assert any("MessageQueue" in q for q in queries)

    # V2 Labels
    assert any("Repository" in q for q in queries)
    assert any("File" in q for q in queries)
    assert any("Class" in q for q in queries)
    assert any("Function" in q for q in queries)
    assert any("Document" in q for q in queries)
    assert any("ADR" in q for q in queries)


def test_schema_queries_enforce_node_id() -> None:
    """Test that every query enforces uniqueness on the 'node_id' property."""
    queries = get_schema_queries()
    for query in queries:
        assert "REQUIRE n.node_id IS UNIQUE" in query
