# backend/core/events/broker.py
#
# This file manages the async connection to the Apache Kafka broker.

import logging

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)


class BrokerConnectionError(Exception):
    """Raised when the broker fails to connect."""

    pass


class EventBroker:
    """
    Manages the lifecycle and connection state of the event broker (Kafka).
    To be injected into FastAPI lifespan events and Health check routers.
    """

    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None
        self._connected: bool = False

    async def connect(self) -> None:
        """Initialize the Kafka producer and connect to the broker."""
        try:
            logger.info(f"Connecting to event broker at {self.bootstrap_servers}...")
            self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self._producer.start()
            self._connected = True
            logger.info("Successfully connected to event broker.")
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to event broker: {str(e)}")
            raise BrokerConnectionError(f"Kafka connection failed: {str(e)}") from e

    async def disconnect(self) -> None:
        """Gracefully shutdown the Kafka producer."""
        if self._producer and self._connected:
            logger.info("Disconnecting from event broker...")
            await self._producer.stop()
            self._connected = False
            logger.info("Successfully disconnected from event broker.")

    def is_connected(self) -> bool:
        """Return the current connection state for health checks."""
        return self._connected


# Global singleton to be attached to FastAPI lifespan
event_broker = EventBroker(bootstrap_servers="localhost:9092")
