# tests/unit/structural/test_code_consumer.py

# This file contains unit tests for the Code Entity Event Consumer (US-6.3),
# verifying AST events translate to structural Neo4j graph nodes and edges.

from unittest.mock import MagicMock

import pytest

from backend.models.events import DependencyDetected, EntityExtracted
from etl.graph_builder.code_consumer import CodeGraphConsumer


@pytest.fixture
def mock_mutation_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def code_consumer(mock_mutation_service: MagicMock) -> CodeGraphConsumer:
    return CodeGraphConsumer(mutation_service=mock_mutation_service)


@pytest.mark.asyncio
async def test_handle_entity_extracted(
    code_consumer: CodeGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify EntityExtracted creates File, Class/Function, and a CONTAINS edge."""
    event = EntityExtracted(
        repository_id=1,
        file_path="src/main.py",
        entity_type="Class",
        name="AuthService",
        docstring="Handles auth.",
    )

    await code_consumer.handle_entity_extracted(event)

    # 1. Assert File Node Upserted
    mock_mutation_service.upsert_node.assert_any_call(
        "File", {"node_id": "file:1:src/main.py", "name": "main.py", "repository_id": 1}
    )

    # 2. Assert Class Node Upserted
    mock_mutation_service.upsert_node.assert_any_call(
        "Class",
        {
            "node_id": "class:1:src/main.py:AuthService",
            "name": "AuthService",
            "docstring": "Handles auth.",
        },
    )

    # 3. Assert CONTAINS Edge Upserted (with ADR-026 provenance)
    upsert_edge_calls = mock_mutation_service.upsert_edge.call_args_list
    assert len(upsert_edge_calls) == 1

    args, kwargs = upsert_edge_calls[0]
    assert args[0] == "file:1:src/main.py"
    assert args[1] == "class:1:src/main.py:AuthService"
    assert args[2] == "CONTAINS"
    assert "source_system" in args[3]
    assert "source_uri" in args[3]


@pytest.mark.asyncio
async def test_handle_dependency_detected(
    code_consumer: CodeGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify DependencyDetected creates the target dependency and a DEPENDS_ON edge."""
    event = DependencyDetected(
        repository_id=1,
        file_path="requirements.txt",
        package_manager="pip",
        package_name="pydantic",
        version_constraint=">=2.0",
    )

    await code_consumer.handle_dependency_detected(event)

    # Assert Edge Upserted
    upsert_edge_calls = mock_mutation_service.upsert_edge.call_args_list
    assert len(upsert_edge_calls) == 1

    args, kwargs = upsert_edge_calls[0]
    assert args[2] == "DEPENDS_ON"
    assert args[3]["source_system"] == "manifest_parser"
    assert args[3]["source_uri"] == "requirements.txt"
