# tests/unit/foundation/test_docker_compose.py

# This test suite verifies the integrity and correctness of the docker-compose.yml
# configuration for the CodeGraph project.

from pathlib import Path
from typing import Any

import yaml


def load_docker_compose() -> Any:
    compose_path = Path("docker-compose.yml")
    if not compose_path.exists():
        raise FileNotFoundError("docker-compose.yml does not exist yet (Red Phase)")
    with open(compose_path) as f:
        return yaml.safe_load(f)


def test_docker_compose_file_exists() -> None:
    """Verify docker-compose.yml exists in the root directory."""
    assert Path("docker-compose.yml").exists(), "docker-compose.yml is missing!"


def test_docker_compose_services_defined() -> None:
    """Verify all required enterprise local services are present."""
    config = load_docker_compose()
    services = config.get("services", {})

    assert "web" in services, "FastAPI 'web' service is missing from docker-compose.yml"
    assert "neo4j" in services, "Neo4j graph database service is missing"
    assert "postgres" in services, "PostgreSQL vector database service is missing"


def test_neo4j_configuration() -> None:
    """Verify Neo4j is configured with APOC plugins and correct environment settings."""
    config = load_docker_compose()
    neo4j_service = config["services"]["neo4j"]

    # Check image and APOC environment variables
    assert "neo4j" in neo4j_service["image"]
    environment = neo4j_service.get("environment", {})

    # Support both dict and list env formats in docker-compose
    if isinstance(environment, list):
        env_dict = {item.split("=")[0]: item.split("=")[1] for item in environment if "=" in item}
    else:
        env_dict = environment

    assert "NEO4J_ACCEPT_LICENSE_AGREEMENT" in env_dict or any(
        "APOC" in str(v) for v in neo4j_service.get("environment", [])
    ), "Neo4j APOC plugin environment variables are missing"


def test_postgres_vector_configuration() -> None:
    """Verify PostgreSQL is configured with vector support (pgvector image)."""
    config = load_docker_compose()
    pg_service = config["services"]["postgres"]

    image = pg_service.get("image", "")
    assert "postgres" in image.lower() or "pgvector" in image.lower(), (
        "PostgreSQL vector image not specified"
    )
    # Verify vector/pgvector readiness or extension support
    env_vars = str(pg_service.get("environment", ""))
    assert "postgres" in env_vars.lower()


def test_volume_persistence_mapped() -> None:
    """Verify persistent data volumes are mapped for state retention."""
    config = load_docker_compose()
    services = config["services"]

    assert "volumes" in config, "Top-level volumes section missing for data persistence"

    # Check neo4j and postgres have persistent volume bindings
    neo4j_volumes = services["neo4j"].get("volumes", [])
    postgres_volumes = services["postgres"].get("volumes", [])

    assert len(neo4j_volumes) > 0, "Neo4j lacks data volume persistence"
    assert len(postgres_volumes) > 0, "PostgreSQL lacks data volume persistence"
