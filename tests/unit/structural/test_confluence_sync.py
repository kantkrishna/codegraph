# tests/unit/structural/test_confluence_sync.py

# Tests for US-5.3 AC4 (Emitting DocumentationUpdated events) & Scheduling.

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.domain.events.ingestion import DocumentationUpdatedEvent
from etl.scheduler.confluence_sync import ConfluenceSyncJob


@pytest.mark.asyncio
async def test_sync_job_emits_events() -> None:
    mock_client = AsyncMock()
    mock_client.fetch_pages_since.return_value = [
        {"id": "1", "title": "Runbook", "body": "<h1>Runbook</h1>", "url": "/wiki/1"}
    ]
    mock_publisher = MagicMock()

    job = ConfluenceSyncJob(client=mock_client, publisher=mock_publisher)
    await job.run_sync()

    # Assert state was updated and event published
    assert job.last_sync_time is not None
    mock_publisher.publish.assert_called_once()

    event = mock_publisher.publish.call_args[0][0]
    assert isinstance(event, DocumentationUpdatedEvent)
    assert event.data.document_type == "confluence"
