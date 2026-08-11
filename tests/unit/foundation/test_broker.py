# tests/unit/foundation/test_broker.py
#
# This file contains unit tests for the EventBroker connection manager (US-3.1).

from unittest.mock import AsyncMock, patch

import pytest

from backend.core.events.broker import BrokerConnectionError, EventBroker


@pytest.mark.asyncio
async def test_event_broker_connects_successfully() -> None:
    """Verify the broker initiates connection and updates state."""
    broker = EventBroker(bootstrap_servers="localhost:9092")

    with patch("backend.core.events.broker.AIOKafkaProducer", autospec=True) as MockProducer:
        mock_instance = MockProducer.return_value
        mock_instance.start = AsyncMock()

        await broker.connect()

        mock_instance.start.assert_awaited_once()
        assert broker.is_connected() is True


@pytest.mark.asyncio
async def test_event_broker_handles_connection_failure() -> None:
    """Verify that connection failures are caught and raised gracefully."""
    broker = EventBroker(bootstrap_servers="localhost:9092")

    with patch("backend.core.events.broker.AIOKafkaProducer") as MockProducer:
        mock_instance = MockProducer.return_value
        mock_instance.start = AsyncMock(side_effect=Exception("Kafka unreachable"))

        with pytest.raises(BrokerConnectionError):
            await broker.connect()

        assert broker.is_connected() is False


@pytest.mark.asyncio
async def test_event_broker_disconnects_gracefully() -> None:
    """Verify the broker stops the producer and updates state."""
    broker = EventBroker(bootstrap_servers="localhost:9092")

    with patch("backend.core.events.broker.AIOKafkaProducer", autospec=True) as MockProducer:
        mock_instance = MockProducer.return_value
        mock_instance.start = AsyncMock()
        mock_instance.stop = AsyncMock()

        await broker.connect()
        assert broker.is_connected() is True

        await broker.disconnect()
        mock_instance.stop.assert_awaited_once()
        assert broker.is_connected() is False
