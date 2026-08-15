# etl/graph_builder/routers.py

# Registers the Graph Builder consumers with the Event Bus (Kafka/Redis).

from backend.core.events.consumer import EventConsumer
from backend.graph.mutation_service import GraphMutationService
from etl.graph_builder.code_consumer import CodeGraphConsumer
from etl.graph_builder.doc_consumer import DocGraphConsumer


def register_graph_consumers(
    code_consumer: EventConsumer,
    doc_consumer: EventConsumer,
    mutation_service: GraphMutationService,
) -> None:
    """Maps Kafka event types to the Graph Consumer methods."""

    code_graph_handler = CodeGraphConsumer(mutation_service)
    doc_graph_handler = DocGraphConsumer(mutation_service)

    # Map Code/AST Events (US-6.3)
    code_consumer.register("EntityExtracted", code_graph_handler.handle_entity_extracted)
    code_consumer.register("DependencyDetected", code_graph_handler.handle_dependency_detected)

    # Map Documentation Events (US-6.4)
    doc_consumer.register("DocumentationUpdated", doc_graph_handler.handle_documentation_updated)
    doc_consumer.register("ADRCreated", doc_graph_handler.handle_adr_created)
    doc_consumer.register("DocumentationLinked", doc_graph_handler.handle_documentation_linked)
