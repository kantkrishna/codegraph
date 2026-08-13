# etl/connectors/markdown/worker.py

# Orchestration worker that consumes FileDiscovered events, processes Markdown/ADRs,
# and publishes the structured engineering knowledge to the Event Bus.

import uuid
from typing import Any, Protocol

from backend.domain.events.ingestion import ADRCreated, DocumentationUpdated, FileDiscovered
from etl.connectors.markdown.adr_parser import extract_decision, extract_status, is_adr
from etl.connectors.markdown.parser import normalize_path, parse_markdown, strip_invalid_chars


class EventPublisher(Protocol):
    """Protocol defining the interface for publishing events."""

    def publish(self, event: Any) -> None: ...


class MarkdownWorker:
    def __init__(self, publisher: EventPublisher) -> None:
        self.publisher = publisher

    def process_event(self, event: FileDiscovered) -> None:
        """Processes a discovered file and emits the appropriate documentation event."""
        if not event.file_path.endswith(".md"):
            return  # US-5.1 AC1: Filter for .md extension

        clean_path = normalize_path(event.file_path)
        clean_content = strip_invalid_chars(event.content)

        metadata, body = parse_markdown(clean_content)

        event_id = str(uuid.uuid4())
        source = "markdown_worker"

        # US-5.2 AC1 & AC3: ADR routing
        if is_adr(clean_path):
            status = extract_status(body)
            decision = extract_decision(body)
            out_event = ADRCreated(
                id=event_id,
                source=source,
                repository=event.repository,
                file_path=clean_path,
                metadata=metadata,
                content=body,
                status=status,
                decision=decision,
            )
        else:
            # US-5.1 AC4: Standard Doc Routing
            out_event = DocumentationUpdated(  # type: ignore[assignment]
                id=event_id,
                source=source,
                repository=event.repository,
                file_path=clean_path,
                metadata=metadata,
                content=body,
            )

        self.publisher.publish(out_event)
