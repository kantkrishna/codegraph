# etl/graph_builder/doc_linker.py

# Downstream worker that inspects document events and links them to the Graph (US-5.4).

import re
from typing import Any, Protocol

from backend.domain.events.ingestion import (
    DocumentationLinkedEvent,
    DocumentationLinkedPayload,
    DocumentationUpdatedEvent,
)
from etl.graph_builder.lookup import Neo4jEntityLookupService


class EventPublisher(Protocol):
    def publish(self, event: Any) -> None: ...


class DocumentLinkerWorker:
    def __init__(self, lookup_service: Neo4jEntityLookupService, publisher: EventPublisher) -> None:
        self.lookup_service = lookup_service
        self.publisher = publisher
        # US-5.4 AC2 heuristics: Captures things like "PaymentService" or "AuthAPI"
        self.heuristic_pattern = re.compile(r"\b[A-Z][a-zA-Z0-9]*(?:Service|API|DB)\b")

    def extract_heuristics(self, content: str) -> list[str]:
        """Extracts potential software entity names from raw text."""
        matches = self.heuristic_pattern.findall(content)
        return list(set(matches))

    async def process_event(self, event: DocumentationUpdatedEvent) -> None:
        """Processes doc events and publishes linkage events if Neo4j nodes exist."""
        content = getattr(event.data, "content", "")
        if not content:
            return

        potential_entities = self.extract_heuristics(content)

        for entity_name in potential_entities:
            # AC3: Direct Neo4j Query
            node_id = await self.lookup_service.find_entity_node_id(entity_name)

            if node_id:
                # AC4: Emit DocumentationLinked
                payload = DocumentationLinkedPayload(
                    doc_id=event.data.document_url,
                    node_id=node_id,
                    entity_name=entity_name,
                    confidence=0.85,  # Heuristic confidence score
                )
                link_event = DocumentationLinkedEvent(source="document_linker_worker", data=payload)
                self.publisher.publish(link_event)
