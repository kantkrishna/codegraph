# backend/core/events/consumer.py
#
# This file implements the EventConsumer, handling event routing,
# OpenTelemetry context extraction, and Dead Letter Queue (DLQ) mechanics (US-3.3, US-3.4).

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka import AIOKafkaConsumer
from opentelemetry import propagate, trace

from backend.core.events.broker import EventBroker
from backend.domain.events.base import CodeGraphEvent

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# Type alias for our asynchronous event handler functions
EventHandler = Callable[[Any], Awaitable[None]]


class EventConsumer:
    """
    Consumes events from a Kafka topic, routes them to registered handlers,
    and manages exceptions by routing failed messages to a DLQ.
    """

    def __init__(
        self,
        broker: EventBroker,
        topic: str,
        group_id: str,
        parser: Callable[[dict[str, Any]], CodeGraphEvent[Any]],
    ) -> None:
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.parser = parser
        self.handlers: dict[str, EventHandler] = {}
        self._consumer: AIOKafkaConsumer | None = None

    def register(self, event_type: str, handler: EventHandler) -> None:
        """Register an async function to handle a specific event type."""
        self.handlers[event_type] = handler

    async def start(self) -> None:
        """Starts the Kafka consumer loop (Requires actual Kafka connection)."""
        logger.info(f"Starting consumer for {self.topic} (Group: {self.group_id})")
        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.broker.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=False,
        )
        await self._consumer.start()
        try:
            async for msg in self._consumer:
                await self.process_message(msg)
                await self._consumer.commit()
        finally:
            await self._consumer.stop()

    async def process_message(self, msg: Any) -> None:
        """
        Core logic to extract trace context, parse JSON, route to handler,
        and manage DLQ fallbacks. Segregated from start() for strict unit testing.
        """
        # US-3.3 AC3: Extract OTel Context from headers
        carrier = (
            {k: v.decode("utf-8") for k, v in msg.headers} if getattr(msg, "headers", None) else {}
        )
        ctx = propagate.extract(carrier)

        with tracer.start_as_current_span(f"consume_{self.topic}", context=ctx) as span:
            event_id = "unknown"
            raw_payload = msg.value.decode("utf-8") if isinstance(msg.value, bytes) else ""

            try:
                # 1. Parse payload
                payload_dict = json.loads(raw_payload)
                event_id = payload_dict.get("id", "unknown")
                event = self.parser(payload_dict)

                span.set_attribute("event.id", str(event.id))
                span.set_attribute("event.type", event.type)

                # 2. Route to Handler
                handler = self.handlers.get(event.type)
                if not handler:
                    logger.warning(f"No handler registered for event type: {event.type}")
                    return

                await handler(event)

            except Exception as e:
                # US-3.4 AC1 & AC2: Unhandled exception -> Log -> Send to DLQ
                span.record_exception(e)
                logger.error(
                    "Consumer exception handling message. Routing to DLQ.",
                    exc_info=True,
                    extra={
                        "topic": self.topic,
                        "dlq_action": "routed",
                        "event_id": event_id,
                        "error": str(e),
                    },
                )

                dlq_topic = f"dlq.{self.topic}"
                if self.broker._producer:
                    await self.broker._producer.send_and_wait(
                        dlq_topic, value=msg.value, headers=getattr(msg, "headers", [])
                    )
                else:
                    logger.critical("Broker producer not initialized! Cannot route to DLQ.")
