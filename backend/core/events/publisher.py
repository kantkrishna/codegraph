# backend/core/events/publisher.py
#
# This file implements the EventPublisher responsible for serializing CodeGraph events,
# injecting OpenTelemetry tracing context, and pushing them to Kafka (US-3.3).

import logging
from typing import Any

from opentelemetry import propagate

from backend.core.events.broker import EventBroker
from backend.domain.events.base import CodeGraphEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes strictly typed CodeGraph events to the message broker."""

    def __init__(self, broker: EventBroker) -> None:
        self.broker = broker

    async def publish(self, topic: str, event: CodeGraphEvent[Any]) -> None:
        """
        Serializes a domain event and publishes it to the specified topic,
        injecting the current distributed trace context into the Kafka headers.
        """
        if not self.broker.is_connected() or not self.broker._producer:
            raise RuntimeError("Cannot publish: Broker is not connected.")

        # US-3.3 AC3: Inject trace IDs into headers
        carrier: dict[str, str] = {}
        propagate.inject(carrier)

        # Kafka requires headers as List[Tuple[str, bytes]]
        kafka_headers: list[tuple[str, bytes]] = [
            (k, v.encode("utf-8")) for k, v in carrier.items()
        ]

        payload = event.model_dump_json().encode("utf-8")

        await self.broker._producer.send_and_wait(topic, value=payload, headers=kafka_headers)

        logger.info(
            f"Published event to {topic}",
            extra={"event_id": str(event.id), "event_type": event.type},
        )
