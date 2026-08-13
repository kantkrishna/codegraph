# tests/unit/structural/test_doc_linker.py

# Tests for US-5.4 AC1, AC2, AC4 (Worker orchestrating the linking).

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.domain.events.ingestion import (
    DocumentationLinkedEvent,
    DocumentationUpdatedEvent,
    DocumentationUpdatedPayload,
)
from etl.graph_builder.doc_linker import DocumentLinkerWorker


@pytest.mark.asyncio
async def test_worker_extracts_and_links() -> None:
    mock_lookup = AsyncMock()
    mock_lookup.find_entity_node_id.return_value = "neo-456"
    mock_publisher = MagicMock()

    worker = DocumentLinkerWorker(lookup_service=mock_lookup, publisher=mock_publisher)

    event = DocumentationUpdatedEvent(
        source="wiki",
        data=DocumentationUpdatedPayload(
            document_url="url", document_type="md", repository_url="repo"
        ),
    )
    # AC2: Injecting metadata and content with heuristics
    event.data.content = "This details the AuthService architecture."

    await worker.process_event(event)

    # AC4: Published linking event
    mock_publisher.publish.assert_called_once()
    linked_event = mock_publisher.publish.call_args[0][0]
    assert isinstance(linked_event, DocumentationLinkedEvent)
    assert linked_event.data.entity_name == "AuthService"
    assert linked_event.data.node_id == "neo-456"