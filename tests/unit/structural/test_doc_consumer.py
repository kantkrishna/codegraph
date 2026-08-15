# tests/unit/structural/test_doc_consumer.py

# This file contains unit tests for the Documentation Event Consumer (US-6.4),
# verifying documentation events connect knowledge to the architecture graph.

from unittest.mock import MagicMock

import pytest

from backend.domain.events.ingestion import (
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
    payload = DocumentationUpdatedPayload(document_url="wiki/123", document_type="confluence", repository_url="repo")
    payload.title = "Architecture Overview"
    
    event = DocumentationUpdatedEvent(source="confluence", data=payload)
    await doc_consumer.handle_documentation_updated(event)
    
    mock_mutation_service.upsert_node.assert_called_once_with(
        "Document",
        {"node_id": "doc:wiki/123", "name": "Architecture Overview", "type": "confluence"}
    )

@pytest.mark.asyncio
async def test_handle_documentation_linked(
    doc_consumer: DocGraphConsumer, mock_mutation_service: MagicMock
) -> None:
    """Verify DocumentationLinked creates a DOCUMENTS edge."""
    payload = DocumentationLinkedPayload(doc_id="doc:wiki/123", node_id="srv-auth", entity_name="AuthService", confidence=0.85)
    event = DocumentationLinkedEvent(source="doc_linker", data=payload)
    
    await doc_consumer.handle_documentation_linked(event)
    
    mock_mutation_service.upsert_edge.assert_called_once_with(
        "doc:wiki/123",
        "srv-auth",
        "DOCUMENTS",
        {"source_system": "doc_linker",
            "source_uri": "doc:wiki/123",
            "timestamp": str(event.time), "confidence": 0.85
        }
    )