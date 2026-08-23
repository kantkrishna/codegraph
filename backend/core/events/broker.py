# backend/core/events/broker.py

# This file manages the async connection to the Apache Kafka broker.

import asyncio
import logging
import os

from aiokafka import AIOKafkaProducer

from backend.core.config import settings

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

    async def connect(self, retries: int = 5, delay: float = 3.0) -> None:
        """Initialize the Kafka producer and connect to the broker with retries."""
        resolved_servers = (
            os.getenv("KAFKA_BOOTSTRAP_SERVERS")
            or os.getenv("KAFKA_URL")
            or str(getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
            or "localhost:9092"
        )
        self.bootstrap_servers = str(resolved_servers)

        for attempt in range(1, retries + 1):
            try:
                logger.info(
                    f"Connecting to event broker at {self.bootstrap_servers} (Attempt {attempt}/{retries})..."  # noqa: E501
                )
                self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
                await self._producer.start()
                self._connected = True
                logger.info("Successfully connected to event broker.")
                return
            except Exception as e:
                logger.warning(f"Kafka connection attempt {attempt} failed: {e}")
                if self._producer:
                    try:
                        await self._producer.stop()
                    except Exception:
                        pass
                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    self._connected = False
                    logger.error("Failed to connect to event broker after maximum retries.")
                    raise BrokerConnectionError(f"Kafka connection failed: {str(e)}") from e

    async def disconnect(self) -> None:
        if self._producer and self._connected:
            logger.info("Disconnecting from event broker...")
            await self._producer.stop()
            self._connected = False
            logger.info("Successfully disconnected from event broker.")

    def is_connected(self) -> bool:
        return self._connected


event_broker = EventBroker(bootstrap_servers="localhost:9092")
