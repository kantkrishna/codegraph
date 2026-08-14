# backend/graph/mutation_service.py

# This file defines the GraphMutationService, a centralized abstraction for executing
# idempotent graph writes (MERGE) while enforcing strict V2 schemas and provenance tracking.

from typing import Any

from neo4j import Driver

from backend.core.decorators import with_neo4j_retries


class GraphMutationService:
    # Strict allowance lists to prevent Cypher injection on dynamic labels/edges
    ALLOWED_LABELS = frozenset(
        {
            "Service",
            "API",
            "Database",
            "MessageQueue",  # V1
            "Repository",
            "File",
            "Class",
            "Function",
            "Document",
            "ADR",  # V2
        }
    )

    ALLOWED_EDGES = frozenset(
        {
            "CALLS",
            "EXPOSES",
            "READS",
            "WRITES",
            "PUBLISHES",
            "SUBSCRIBES_TO",  # V1
            "CONTAINS",
            "IMPLEMENTS",
            "DOCUMENTS",
            "DEPENDS_ON",
            "IMPORTS",  # V2
        }
    )

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    @with_neo4j_retries(max_retries=3, base_delay=0.5)
    def upsert_node(self, label: str, properties: dict[str, Any]) -> None:
        """
        Idempotently inserts or updates a Node.
        """
        if label not in self.ALLOWED_LABELS:
            raise ValueError(f"Invalid node label: {label}")
        if "node_id" not in properties:
            raise ValueError("node_id is required property for all graph nodes.")

        # Cypher parameters ($props) protect against injection for properties.
        # F-strings are used for Labels because Neo4j does not support parameterized labels.
        query = f"""
        MERGE (n:{label} {{node_id: $props.node_id}})
        SET n += $props
        """
        with self.driver.session() as session:
            session.run(query, props=properties)

    @with_neo4j_retries(max_retries=3, base_delay=0.5)
    def upsert_edge(
        self, source_id: str, target_id: str, rel_type: str, properties: dict[str, Any]
    ) -> None:
        """
        Idempotently inserts or updates an Edge between two existing Nodes.
        Enforces ADR-026 strict source provenance tracking.
        """
        if rel_type not in self.ALLOWED_EDGES:
            raise ValueError(f"Invalid relationship type: {rel_type}")

        required_provenance = {"source_system", "source_uri", "timestamp"}
        missing = required_provenance - properties.keys()
        if missing:
            raise ValueError(f"Missing provenance properties: {missing}. Required per ADR-026.")

        query = f"""
        MATCH (a {{node_id: $source_id}})
        MATCH (b {{node_id: $target_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        """
        with self.driver.session() as session:
            session.run(query, source_id=source_id, target_id=target_id, props=properties)
