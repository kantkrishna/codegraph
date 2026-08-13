# tests/unit/structural/test_markdown_worker.py

# Tests for US-5.1 AC1, AC4 and US-5.2 AC3: The orchestration worker.

from typing import Any, cast

import pytest

from backend.domain.events.ingestion import ADRCreated, DocumentationUpdated, FileDiscovered
from etl.connectors.markdown.worker import MarkdownWorker


class MockPublisher:
    def __init__(self) -> None:
        self.published_events: list[Any] = []

    def publish(self, event: Any) -> None:
        self.published_events.append(event)


@pytest.fixture
def worker() -> MarkdownWorker:
    return MarkdownWorker(publisher=MockPublisher())


def test_worker_ignores_non_markdown(worker: MarkdownWorker) -> None:
    event = FileDiscovered(
        id="1", source="git", repository="repo-1", file_path="main.py", content="print('hi')"
    )
    worker.process_event(event)

    # Cast back to MockPublisher to satisfy MyPy Protocol bounds
    mock_publisher = cast(MockPublisher, worker.publisher)
    assert len(mock_publisher.published_events) == 0


def test_worker_publishes_documentation_updated(worker: MarkdownWorker) -> None:
    content = "---\ntitle: API\n---\n# Docs"
    event = FileDiscovered(
        id="2", source="git", repository="repo-1", file_path="docs/api.md", content=content
    )
    worker.process_event(event)

    mock_publisher = cast(MockPublisher, worker.publisher)
    published = mock_publisher.published_events

    assert len(published) == 1
    assert isinstance(published[0], DocumentationUpdated)
    assert published[0].metadata["title"] == "API"
    assert published[0].file_path == "docs/api.md"


def test_worker_publishes_adr_created(worker: MarkdownWorker) -> None:
    content = "## Status\nAccepted\n## Decision\nNeo4j."
    event = FileDiscovered(
        id="3", source="git", repository="repo-1", file_path="docs/adr/001.md", content=content
    )
    worker.process_event(event)

    mock_publisher = cast(MockPublisher, worker.publisher)
    published = mock_publisher.published_events

    assert len(published) == 1
    assert isinstance(published[0], ADRCreated)
    assert published[0].status == "Accepted"

    # Satisfy MyPy Optional[str] bounds
    assert published[0].decision is not None
    assert "Neo4j" in published[0].decision
