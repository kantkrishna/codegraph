# tests/unit/foundation/test_health.py

# This test file is used to verify that the health check endpoint correctly reports the
# status of the application and its dependencies.

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.api.main import app

# Global client is fine here if we don't pass it as an argument
client = TestClient(app)


@patch("backend.api.routers.health.verify_neo4j_connection")
@patch("backend.api.routers.health.verify_postgres_connection")
def test_health_check_ok(mock_pg: MagicMock, mock_neo4j: MagicMock) -> None:
    """Verify health endpoint returns 200 OK when databases are connected."""
    mock_pg.return_value = True
    mock_neo4j.return_value = True

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["databases"]["neo4j"] == "connected"
    assert data["databases"]["postgres"] == "connected"


@patch("backend.api.routers.health.verify_neo4j_connection")
@patch("backend.api.routers.health.verify_postgres_connection")
def test_health_check_db_failure(mock_pg: MagicMock, mock_neo4j: MagicMock) -> None:
    """Verify health endpoint returns 503 if a database is down."""
    mock_pg.return_value = False
    mock_neo4j.return_value = True

    response = client.get("/health")
    assert response.status_code == 503
    data = response.json()["detail"]
    assert data["status"] == "error"
    assert data["databases"]["postgres"] == "disconnected"
