# etl/graph_builder/lookup.py

# Read-only Cypher query service to verify physical nodes in Neo4j (US-5.4).

from typing import Any, Protocol


# Assuming neo4j driver protocol
class AsyncDriverProtocol(Protocol):
    def session(self) -> Any: ...


class Neo4jEntityLookupService:
    def __init__(self, driver: AsyncDriverProtocol) -> None:
        self.driver = driver

    async def find_entity_node_id(self, entity_name: str) -> str | None:
        """Executes a direct graph query to find if a service/entity exists."""
        query = """
        MATCH (n) 
        WHERE n.name = $name OR $name IN n.aliases
        RETURN elementId(n) AS node_id 
        LIMIT 1
        """
        async with self.driver.session() as session:
            result = await session.run(query, name=entity_name)
            record = await result.single()
            if record:
                return str(record["node_id"])
        return None
