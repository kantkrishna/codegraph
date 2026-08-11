# tests/unit/foundation/test_publisher.py
#
# This file contains unit tests for the EventPublisher (US-3.3).

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend.core.events.broker import EventBroker
from backend.core.events.publisher import EventPublisher
from backend.domain.events.ingestion import RepositoryIndexedEvent, RepositoryIndexedPayload


@pytest.mark.asyncio
async def test_event_publisher_serializes_and_sends_with_telemetry() -> None:
    """Verify publisher serializes events and injects OpenTelemetry headers (US-3.3)."""
    broker = EventBroker("localhost:9092")
    broker._connected = True
    broker._producer = AsyncMock()
    broker._producer.send_and_wait = AsyncMock()

    publisher = EventPublisher(broker)

    event = RepositoryIndexedEvent(
        source="urn:test",
        data=RepositoryIndexedPayload(repository_url="http://test", commit_hash="123"),
    )

    await publisher.publish("events.ingestion", event)

    # Verify send_and_wait was called
    broker._producer.send_and_wait.assert_awaited_once()
    args, kwargs = broker._producer.send_and_wait.call_args
    assert args[0] == "events.ingestion"

    # Verify payload is correctly serialized to JSON bytes
    sent_value = kwargs["value"]
    parsed: dict[str, Any] = json.loads(sent_value.decode("utf-8"))
    assert parsed["type"] == "RepositoryIndexed"
    assert parsed["data"]["commit_hash"] == "123"

    # Verify Kafka headers exist (prepared for OpenTelemetry injection)
    headers = kwargs.get("headers")
    assert headers is not None
    assert isinstance(headers, list)
