# tests/unit/structural/test_mutation_service.py

# This file contains unit tests for the GraphMutationService, ensuring idempotent
# writes and strict provenance property validation.

from unittest.mock import MagicMock

import pytest

from backend.graph.mutation_service import GraphMutationService


@pytest.fixture
def mock_driver() -> MagicMock:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    return driver


@pytest.fixture
def mutation_service(mock_driver: MagicMock) -> GraphMutationService:
    return GraphMutationService(mock_driver)


def test_upsert_node_missing_node_id(mutation_service: GraphMutationService) -> None:
    with pytest.raises(ValueError, match="node_id is required"):
        mutation_service.upsert_node("Class", {"name": "AuthService"})


def test_upsert_node_invalid_label(mutation_service: GraphMutationService) -> None:
    with pytest.raises(ValueError, match="Invalid node label"):
        mutation_service.upsert_node("HackerLabel", {"node_id": "123"})


def test_upsert_node_success(
    mutation_service: GraphMutationService, mock_driver: MagicMock
) -> None:
    props = {"node_id": "file-01", "name": "main.py"}
    mutation_service.upsert_node("File", props)

    session = mock_driver.session.return_value.__enter__.return_value
    session.run.assert_called_once()
    call_args = session.run.call_args[0]

    # Ensure MERGE is used for idempotency
    assert "MERGE (n:File {node_id: $props.node_id})" in call_args[0]
    assert "SET n += $props" in call_args[0]


def test_upsert_edge_missing_provenance(mutation_service: GraphMutationService) -> None:
    props = {"timestamp": "2026-08-14"}  # Missing source_system and source_uri
    with pytest.raises(ValueError, match="Missing provenance properties"):
        mutation_service.upsert_edge("file-01", "class-01", "CONTAINS", props)


def test_upsert_edge_invalid_relationship(mutation_service: GraphMutationService) -> None:
    props = {"source_system": "github", "source_uri": "repo/main.py", "timestamp": "2026-08-14"}
    with pytest.raises(ValueError, match="Invalid relationship type"):
        mutation_service.upsert_edge("A", "B", "HACKER_REL", props)


def test_upsert_edge_success(
    mutation_service: GraphMutationService, mock_driver: MagicMock
) -> None:
    props = {"source_system": "github", "source_uri": "repo/main.py", "timestamp": "2026-08-14"}
    mutation_service.upsert_edge("file-01", "class-01", "CONTAINS", props)

    session = mock_driver.session.return_value.__enter__.return_value
    session.run.assert_called_once()
    call_args = session.run.call_args[0]

    # Ensure relationships are MERGED safely
    assert "MERGE (a)-[r:CONTAINS]->(b)" in call_args[0]
    assert "SET r += $props" in call_args[0]
