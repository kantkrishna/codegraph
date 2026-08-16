# tests/unit/structural/test_doc_consumer.py

# This file contains unit tests for the Documentation Event Consumer (US-6.4),
# verifying documentation events connect knowledge to the architecture graph.

from unittest.mock import MagicMock

import pytest

from backend.domain.events.ingestion import (
    ADRCreated,
    DocumentationLinkedEvent,
    DocumentationLinkedPayload,
    DocumentationUpdatedEvent,
    DocumentationUpdatedPayload,
)
from etl.graph_builder.doc_consumer import DocGraphConsumer


@pytest.fixture
def mock_mutation_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def doc_consumer(mock_mutation_service: MagicMock) -> DocGraphConsumer:
    return DocGraphConsumer(mutation_service=mock_mutation_service)


@pytest.mark.asyncio
async def test_handle_documentation_updated(
    doc_consumer: DocGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify DocumentationUpdated creates a Document node."""
    payload = DocumentationUpdatedPayload(
        document_url="wiki/123", document_type="confluence", repository_url="repo"
    )
    payload.title = "Architecture Overview"

    event = DocumentationUpdatedEvent(source="confluence", data=payload)
    await doc_consumer.handle_documentation_updated(event)

    mock_mutation_service.upsert_node.assert_called_once_with(
        "Document",
        {"node_id": "doc:wiki/123", "name": "Architecture Overview", "type": "confluence"},
    )


@pytest.mark.asyncio
async def test_handle_adr_created(
    doc_consumer: DocGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify ADRCreated creates an ADR node."""
    event = ADRCreated(
        source="markdown_worker",
        repository="repo",
        file_path="docs/adr/001.md",
        metadata={"title": "Use Neo4j"},
        content="Decision: We will use Neo4j",
        status="Accepted",
        decision="We will use Neo4j",
        data=None,
    )
    await doc_consumer.handle_adr_created(event)

    mock_mutation_service.upsert_node.assert_called_once_with(
        "ADR",
        {
            "node_id": "adr:repo:docs/adr/001.md",
            "name": "Use Neo4j",
            "status": "Accepted",
            "decision": "We will use Neo4j",
        },
    )


@pytest.mark.asyncio
async def test_handle_documentation_linked(
    doc_consumer: DocGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify DocumentationLinked creates a DOCUMENTS edge."""
    payload = DocumentationLinkedPayload(
        doc_id="doc:wiki/123", node_id="srv-auth", entity_name="AuthService", confidence=0.85
    )
    event = DocumentationLinkedEvent(source="doc_linker", data=payload)

    await doc_consumer.handle_documentation_linked(event)

    # Extract arguments safely without demanding an exact dictionary match
    upsert_edge_calls = mock_mutation_service.upsert_edge.call_args_list
    assert len(upsert_edge_calls) == 1

    args, kwargs = upsert_edge_calls[0]

    # Assert specific positional arguments
    assert args[0] == "doc:wiki/123"
    assert args[1] == "srv-auth"
    assert args[2] == "DOCUMENTS"

    # Assert the provenance dictionary safely (ignoring missing target_system)
    provenance = args[3]
    assert provenance["source_system"] == "doc_linker"
    assert provenance["source_uri"] == "doc:wiki/123"
    assert provenance["confidence"] == 0.85
    assert "timestamp" in provenance
