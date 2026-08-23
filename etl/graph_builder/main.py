# etl/graph_builder/main.py

# This file is responsible for orchestrating the graph building process.
# It handles the ingestion of events, parsing them, and updating the graph accordingly.

import asyncio
import logging

from backend.core.events.broker import event_broker
from backend.core.events.consumer import EventConsumer
from backend.core.logger import setup_logging
from backend.core.telemetry import setup_telemetry
from backend.domain.events.ingestion import parse_ingestion_event
from backend.graph.mutation_service import GraphMutationService
from backend.infrastructure.db import neo4j_driver
from etl.graph_builder.routers import register_graph_consumers

logger = logging.getLogger(__name__)


async def start_graph_builder() -> None:
    setup_logging()
    setup_telemetry(app=None, service_name="codegraph-builder")

    # 1. Connect to Kafka
    await event_broker.connect(retries=10, delay=5.0)

    # 2. Initialize Neo4j Mutation Service
    mutation_service = GraphMutationService(neo4j_driver)

    # 3. Initialize the Kafka Consumer
    consumer = EventConsumer(
        broker=event_broker,
        topic="events.knowledge.extracted",
        group_id="neo4j_graph_builder",
        parser=parse_ingestion_event,
    )

    # 4. Route both Code and Doc events to the single consumer
    register_graph_consumers(consumer, consumer, mutation_service)

    logger.info("Graph Builder Consumer started. Listening for events...")
    await consumer.start()


if __name__ == "__main__":
    asyncio.run(start_graph_builder())
