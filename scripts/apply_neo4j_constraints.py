# scripts/apply_neo4j_constraints.py

# This script applies Neo4j V1 and V2 schema constraints.
# Refactored for testability to separate query generation from execution.

import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


def get_schema_queries() -> list[str]:
    """Generate all constraint queries for V1 and V2 nodes."""
    labels = [
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
    ]
    queries = []
    for label in labels:
        queries.append(
            f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.node_id IS UNIQUE;"
        )
    return queries


def apply_constraints() -> None:
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "codegraph_dev_password")

    print("Applying V1 and V2 constraints...")
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            for query in get_schema_queries():
                print(f"Executing: {query}")
                session.run(query)
    print("Constraints applied successfully.")


if __name__ == "__main__":
    apply_constraints()
