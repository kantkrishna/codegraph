# tests/unit/foundation/test_consumer.py
#
# This file contains unit tests for the EventConsumer, Routing, and DLQ logic (US-3.3, US-3.4).

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend.core.events.broker import EventBroker
from backend.core.events.consumer import EventConsumer
from backend.domain.events.ingestion import parse_ingestion_event


class MockConsumerRecord:
    """Mock representing aiokafka's ConsumerRecord structure."""

    def __init__(self, value: bytes, headers: list[tuple[str, bytes]]):
        self.value = value
        self.headers = headers


@pytest.mark.asyncio
async def test_consumer_routes_to_correct_handler() -> None:
    """Verify consumer parses payload and routes to registered handler (US-3.3)."""
    broker = EventBroker("localhost:9092")
    consumer = EventConsumer(
        broker=broker, topic="events.test", group_id="test-group", parser=parse_ingestion_event
    )

    handler_mock = AsyncMock()
    consumer.register("RepositoryIndexed", handler_mock)

    payload = {
        "source": "urn:test",
        "type": "RepositoryIndexed",
        "data": {"repository_url": "http://test", "commit_hash": "123"},
    }
    msg = MockConsumerRecord(value=json.dumps(payload).encode("utf-8"), headers=[])

    await consumer.process_message(msg)

    handler_mock.assert_awaited_once()
    called_event = handler_mock.call_args[0][0]
    assert called_event.type == "RepositoryIndexed"
    assert called_event.data.commit_hash == "123"


@pytest.mark.asyncio
async def test_consumer_dlq_routing_on_exception(caplog: pytest.LogCaptureFixture) -> None:
    """Verify unhandled exceptions push the raw message to a DLQ and log accurately (US-3.4)."""
    broker = EventBroker("localhost:9092")
    broker._producer = AsyncMock()
    broker._producer.send_and_wait = AsyncMock()

    consumer = EventConsumer(
        broker=broker, topic="events.ingestion", group_id="test-group", parser=parse_ingestion_event
    )

    async def failing_handler(event: Any) -> None:
        raise ValueError("Simulated handler failure")

    consumer.register("RepositoryIndexed", failing_handler)

    event_id = "123e4567-e89b-12d3-a456-426614174000"
    payload = {
        "id": event_id,
        "source": "urn:test",
        "type": "RepositoryIndexed",
        "data": {"repository_url": "http://test", "commit_hash": "abc"},
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    msg = MockConsumerRecord(value=raw_bytes, headers=[("traceparent", b"00-trace-id")])

    # Execute processing (should catch exception internally)
    await consumer.process_message(msg)

    # 1. Verify DLQ Publishing
    broker._producer.send_and_wait.assert_awaited_once()
    args, kwargs = broker._producer.send_and_wait.call_args
    assert args[0] == "dlq.events.ingestion"
    assert kwargs["value"] == raw_bytes
    assert kwargs["headers"] == [("traceparent", b"00-trace-id")]

    # 2. Verify Logging (US-3.4 AC2)
    assert "Routing to DLQ" in caplog.text
    assert "Simulated handler failure" in caplog.text


@pytest.mark.asyncio
async def test_consumer_dlq_routing_on_parse_failure() -> None:
    """Verify invalid JSON also results in safe routing to DLQ."""
    broker = EventBroker("localhost:9092")
    broker._producer = AsyncMock()
    broker._producer.send_and_wait = AsyncMock()

    consumer = EventConsumer(
        broker=broker, topic="events.test", group_id="test-group", parser=parse_ingestion_event
    )

    raw_bytes = b"invalid-json-payload"
    msg = MockConsumerRecord(value=raw_bytes, headers=[])

    await consumer.process_message(msg)

    broker._producer.send_and_wait.assert_awaited_once_with(
        "dlq.events.test", value=raw_bytes, headers=[]
    )
