# etl/graph_builder/doc_consumer.py

# This file consumes Documentation events to link text to the architecture graph.

from backend.domain.events.ingestion import (
    ADRCreated,
    DocumentationLinkedEvent,
    DocumentationUpdatedEvent,
)
from backend.graph.mutation_service import GraphMutationService
from etl.graph_builder.telemetry import with_graph_telemetry


class DocGraphConsumer:
    def __init__(self, mutation_service: GraphMutationService) -> None:
        self.mutation_service = mutation_service

    @with_graph_telemetry("consume_documentation_updated")
    async def handle_documentation_updated(self, event: DocumentationUpdatedEvent) -> None:
        """Translates DocumentationUpdated into Document nodes."""
        node_id = f"doc:{event.data.document_url}"
        name = getattr(event.data, "title", "Untitled Document")

        self.mutation_service.upsert_node(
            "Document", {"node_id": node_id, "name": name, "type": event.data.document_type}
        )

    @with_graph_telemetry("consume_adr_created")
    async def handle_adr_created(self, event: ADRCreated) -> None:
        """Translates ADRCreated into ADR nodes."""
        node_id = f"adr:{event.repository}:{event.file_path}"
        name = event.metadata.get("title", "Untitled ADR") if event.metadata else "Untitled ADR"

        self.mutation_service.upsert_node(
            "ADR",
            {
                "node_id": node_id,
                "name": name,
                "status": event.status or "Unknown",
                "decision": event.decision or "",
            },
        )

    @with_graph_telemetry("consume_documentation_linked")
    async def handle_documentation_linked(self, event: DocumentationLinkedEvent) -> None:
        """Creates the DOCUMENTS edge between the Document and the structural Node."""
        provenance = {
            "source_system": event.source,
            "source_uri": event.data.doc_id,
            "timestamp": str(event.time),
            "confidence": event.data.confidence,
        }

        self.mutation_service.upsert_edge(
            event.data.doc_id, event.data.node_id, "DOCUMENTS", provenance
        )
