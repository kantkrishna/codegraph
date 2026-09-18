# etl/graph_builder/code_consumer.py

# This file defines the CodeGraphConsumer, which consumes events from the ETL pipeline and upserts them into the graph database.
# It handles EntityExtracted, DependencyDetected, and RelationshipExtracted events, ensuring that nodes and edges are created with proper provenance and architectural context.

import os
from datetime import UTC, datetime

from backend.graph.mutation_service import GraphMutationService
from backend.models.events import DependencyDetected, EntityExtracted, RelationshipExtracted
from etl.graph_builder.telemetry import with_graph_telemetry


class CodeGraphConsumer:
    def __init__(self, mutation_service: GraphMutationService) -> None:
        self.mutation_service = mutation_service

    def _extract_service_name(self, file_path: str) -> str | None:
        """Heuristic: Extracts service name from monorepo structures (e.g., src/frontend/...)."""
        parts = file_path.replace("\\", "/").split("/")
        if len(parts) >= 2 and parts[0] == "src":
            return parts[1]
        return None

    @with_graph_telemetry("consume_entity_extracted")
    async def handle_entity_extracted(self, event: EntityExtracted) -> None:
        file_node_id = f"file:{event.repository_id}:{event.file_path}"
        file_name = os.path.basename(event.file_path)
        
        # 1. Upsert base nodes
        self.mutation_service.upsert_node(
            "File", {"node_id": file_node_id, "name": file_name, "repository_id": event.repository_id}
        )
        entity_node_id = f"{event.entity_type.lower()}:{event.repository_id}:{event.file_path}:{event.name}"
        self.mutation_service.upsert_node(
            event.entity_type, {"node_id": entity_node_id, "name": event.name, "docstring": event.docstring or ""}
        )
        
        provenance = {
            "source_system": "ast_parser",
            "source_uri": event.file_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.mutation_service.upsert_edge(file_node_id, entity_node_id, "CONTAINS", provenance)

        # 2. ARCHITECTURAL ABSTRACTION: Link to parent Microservice
        service_name = self._extract_service_name(event.file_path)
        if service_name:
            service_node_id = f"svc:{event.repository_id}:{service_name}"
            self.mutation_service.upsert_node(
                "Service", {"node_id": service_node_id, "name": service_name, "type": "Microservice"}
            )
            # Group the File and Entity under the Service
            self.mutation_service.upsert_edge(file_node_id, service_node_id, "BELONGS_TO", provenance)
            self.mutation_service.upsert_edge(entity_node_id, service_node_id, "BELONGS_TO", provenance)

    @with_graph_telemetry("consume_dependency_detected")
    async def handle_dependency_detected(self, event: DependencyDetected) -> None:
        provenance = {
            "source_system": "manifest_parser",
            "source_uri": event.file_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # FIX: Handle Kubernetes Network Topology
        if event.package_manager == "kubernetes":
            source_service = event.version_constraint
            target_service = event.package_name

            source_node_id = f"svc:{event.repository_id}:{source_service}"
            target_node_id = f"svc:{event.repository_id}:{target_service}"

            self.mutation_service.upsert_node("Service", {"node_id": source_node_id, "name": source_service, "type": "Microservice"})
            self.mutation_service.upsert_node("Service", {"node_id": target_node_id, "name": target_service, "type": "Microservice"})
            
            # Map the cross-service network call
            self.mutation_service.upsert_edge(source_node_id, target_node_id, "DEPENDS_ON", provenance)
            return

    @with_graph_telemetry("consume_relationship_extracted")
    async def handle_relationship_extracted(self, event: RelationshipExtracted) -> None:
        source_file_id = f"file:{event.repository_id}:{event.source_file}"
        target_node_id = f"module:{event.target_module}"
        
        self.mutation_service.upsert_node(
            "Service", {"node_id": target_node_id, "name": event.target_module}
        )
        provenance = {
            "source_system": event.source,
            "source_uri": event.source_file,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.mutation_service.upsert_edge(source_file_id, target_node_id, event.relationship_type, provenance)