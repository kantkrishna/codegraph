# etl/scheduler/confluence_sync.py

# Orchestrates the Confluence pull pipeline and emits standard events (US-5.3).

from datetime import UTC, datetime
from typing import Any, Protocol

from backend.domain.events.ingestion import DocumentationUpdatedEvent, DocumentationUpdatedPayload
from etl.connectors.confluence.client import ConfluenceCloudClient
from etl.connectors.confluence.converter import html_to_markdown


class EventPublisher(Protocol):
    def publish(self, event: Any) -> None: ...


class ConfluenceSyncJob:
    def __init__(self, client: ConfluenceCloudClient, publisher: EventPublisher) -> None:
        self.client = client
        self.publisher = publisher
        # Baseline sync defaults to start of the epoch for MVP
        self.last_sync_time = "2020-01-01T00:00:00Z"

    async def run_sync(self) -> None:
        """Executes an incremental pull, converts content, and publishes events."""
        pages = await self.client.fetch_pages_since(self.last_sync_time)

        for page in pages:
            markdown_content = html_to_markdown(page["body"])

            payload = DocumentationUpdatedPayload(
                document_url=page.get("url", ""),
                document_type="confluence",
                repository_url="urn:codegraph:confluence",
            )
            # Extending dynamic payload with title and body
            payload.content = markdown_content
            payload.title = page["title"]

            event = DocumentationUpdatedEvent(source="confluence_connector", data=payload)
            self.publisher.publish(event)

        self.last_sync_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
