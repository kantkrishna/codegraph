# etl/graph_builder/doc_consumer.py

# This file consumes Documentation events to link text to the architecture graph.

from typing import Any

from backend.domain.events.ingestion import (
    ADRCreated,
    DocumentationLinkedEvent,
)
from backend.graph.mutation_service import GraphMutationService
from etl.graph_builder.telemetry import with_graph_telemetry


class DocGraphConsumer:
    def __init__(self, mutation_service: GraphMutationService) -> None:
        self.mutation_service = mutation_service

    @with_graph_telemetry("consume_documentation_updated")
    async def handle_documentation_updated(self, event: Any) -> None:
        """Translates DocumentationUpdated events into Document nodes."""
        if hasattr(event, "file_path"):
            node_id = f"doc:{getattr(event, 'repository', 'unknown')}:{event.file_path}"
            name = (event.metadata.get("title") if getattr(event, "metadata", None) else None) or event.file_path
            doc_type = "markdown"
        elif getattr(event, "data", None):
            node_id = f"doc:{event.data.document_url}"
            name = getattr(event.data, "title", "Untitled Document") or "Untitled Document"
            doc_type = getattr(event.data, "document_type", "document")
        else:
            node_id = f"doc:{getattr(event, 'id', 'unknown')}"
            name = "Untitled Document"
            doc_type = "document"

        self.mutation_service.upsert_node(
            "Document", {"node_id": node_id, "name": name, "type": doc_type}
        )

    @with_graph_telemetry("consume_adr_created")
    async def handle_adr_created(self, event: ADRCreated) -> None:
        """Translates ADRCreated events into ADR nodes."""
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
        """Creates DOCUMENTS edges between Document/ADR and structural Nodes."""
        provenance = {
            "source_system": event.source,
            "source_uri": event.data.doc_id,
            "timestamp": str(event.time),
            "confidence": event.data.confidence,
        }
        self.mutation_service.upsert_edge(
            event.data.doc_id, event.data.node_id, "DOCUMENTS", provenance
        )