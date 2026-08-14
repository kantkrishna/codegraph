# scripts/validate_neo4j_schema.py

# This script validates both the V1 architecture schema and the V2 code/doc schema
# by asserting mock data can be written and queried successfully.

import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


def validate_schema() -> None:
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "codegraph_dev_password")
    auth_tuple: tuple[str, str] = (user, password)

    # Insert V1 Architecture + V2 Code & Docs
    insert_query = """
    MERGE (s:Service {node_id: "srv-001", name: "PaymentService"})
    MERGE (api:API {node_id: "api-001", name: "POST /checkout"})
    
    // V2 Expanded Ontology
    MERGE (repo:Repository {node_id: "repo-001", name: "payments-backend"})
    MERGE (file:File {node_id: "file-001", name: "checkout.py"})
    MERGE (doc:ADR {node_id: "adr-001", name: "ADR-01: Use Stripe"})
    
    // Edges
    MERGE (repo)-[:CONTAINS {source_system: "github", timestamp: "2026-08-14"}]->(file)
    MERGE (s)-[:CALLS {source_system: "manual", timestamp: "2026-08-14"}]->(api)
    MERGE (doc)-[:DOCUMENTS {source_system: "github", timestamp: "2026-08-14"}]->(s)
    """

    validation_query = """
    MATCH (doc:ADR)-[r1:DOCUMENTS]->(s:Service)-[r2:CALLS]->(api:API)
    RETURN doc.name AS adr, s.name AS service, api.name AS api
    """

    with GraphDatabase.driver(uri, auth=auth_tuple) as driver:
        with driver.session() as session:
            print("Inserting V1 and V2 mock data...")
            session.run(insert_query)

            print("Executing traversal query...")
            result = session.run(validation_query)
            records_found = False
            for record in result:
                records_found = True
                print(
                    f"ADR [{record['adr']}] -> Service [{record['service']}] -> API [{record['api']}]"  # noqa: E501
                )

            if records_found:
                print("Validation PASSED: V1/V2 Schemas correctly mapped and queried.")
            else:
                print("Validation FAILED: No dependencies found.")


if __name__ == "__main__":
    validate_schema()
