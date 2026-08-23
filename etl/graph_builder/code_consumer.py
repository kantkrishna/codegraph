# etl/graph_builder/code_consumer.py

# This file consumes AST and Dependency events to build the structural code graph.

import os
from datetime import UTC, datetime

from backend.graph.mutation_service import GraphMutationService
from backend.models.events import DependencyDetected, EntityExtracted, RelationshipExtracted
from etl.graph_builder.telemetry import with_graph_telemetry


class CodeGraphConsumer:
    def __init__(self, mutation_service: GraphMutationService) -> None:
        self.mutation_service = mutation_service

    @with_graph_telemetry("consume_entity_extracted")
    async def handle_entity_extracted(self, event: EntityExtracted) -> None:
        """Translates EntityExtracted events into File, Class/Function nodes & CONTAINS edges."""
        file_node_id = f"file:{event.repository_id}:{event.file_path}"
        file_name = os.path.basename(event.file_path)

        # 1. Upsert the File Node
        self.mutation_service.upsert_node(
            "File",
            {"node_id": file_node_id, "name": file_name, "repository_id": event.repository_id},
        )

        # 2. Upsert the Entity Node (Class or Function)
        entity_node_id = (
            f"{event.entity_type.lower()}:{event.repository_id}:{event.file_path}:{event.name}"  # noqa: E501
        )
        self.mutation_service.upsert_node(
            event.entity_type,
            {"node_id": entity_node_id, "name": event.name, "docstring": event.docstring or ""},
        )

        # 3. Create the CONTAINS edge
        provenance = {
            "source_system": "ast_parser",
            "source_uri": event.file_path,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.mutation_service.upsert_edge(file_node_id, entity_node_id, "CONTAINS", provenance)

    @with_graph_telemetry("consume_dependency_detected")
    async def handle_dependency_detected(self, event: DependencyDetected) -> None:
        """Translates DependencyDetected events into DEPENDS_ON edges."""
        file_node_id = f"file:{event.repository_id}:{event.file_path}"
        package_node_id = f"pkg:{event.package_manager}:{event.package_name}"

        # Ensure target node exists
        self.mutation_service.upsert_node(
            "Service",  # Fallback ontology for external packages
            {"node_id": package_node_id, "name": event.package_name},
        )

        provenance = {
            "source_system": "manifest_parser",
            "source_uri": event.file_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "version_constraint": event.version_constraint or "",
        }
        self.mutation_service.upsert_edge(file_node_id, package_node_id, "DEPENDS_ON", provenance)

    @with_graph_telemetry("consume_relationship_extracted")
    async def handle_relationship_extracted(self, event: RelationshipExtracted) -> None:
        """Translates RelationshipExtracted events into IMPORTS edges."""
        source_file_id = f"file:{event.repository_id}:{event.source_file}"
        target_node_id = f"module:{event.target_module}"

        # Ensure target node exists (using Service as a fallback label for external/other modules)
        self.mutation_service.upsert_node(
            "Service",
            {"node_id": target_node_id, "name": event.target_module},
        )

        provenance = {
            "source_system": event.source,
            "source_uri": event.source_file,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.mutation_service.upsert_edge(
            source_file_id, target_node_id, event.relationship_type, provenance
        )
