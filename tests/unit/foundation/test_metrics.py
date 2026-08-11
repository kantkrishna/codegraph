# tests/unit/foundation/test_metrics.py
#
# This file contains unit tests for Prometheus metrics exposure and middleware tracking.

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# These imports will fail during the Red Phase
from backend.api.middleware.metrics_middleware import MetricsMiddleware
from backend.api.routers import system


@pytest.fixture
def metrics_app() -> FastAPI:
    """Creates a fresh FastAPI instance with the metrics middleware and router attached."""
    app = FastAPI()
    app.add_middleware(MetricsMiddleware)
    app.include_router(system.router)

    @app.get("/test-route")
    def test_route() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/error-route")
    def error_route() -> dict[str, str]:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="bad request")

    return app


@pytest.fixture
def client(metrics_app: FastAPI) -> TestClient:
    return TestClient(metrics_app)


def test_metrics_endpoint_exists(client: TestClient) -> None:
    """AC 1: Verify /metrics endpoint exists and returns Prometheus text format."""
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_http_request_metrics_recorded(client: TestClient) -> None:
    """AC 2 & 3: Verify HTTP requests track total count and duration by route and status."""
    # Trigger route hits to populate metrics
    client.get("/test-route")
    client.get("/error-route")

    response = client.get("/metrics")
    metrics_text = response.text

    # AC 3: Check counter and exact labels
    assert "http_requests_total" in metrics_text
    assert 'path="/test-route"' in metrics_text
    assert 'status_code="200"' in metrics_text

    assert 'path="/error-route"' in metrics_text
    assert 'status_code="400"' in metrics_text

    # AC 2: Check histogram
    assert "http_request_duration_seconds_bucket" in metrics_text
    assert "http_request_duration_seconds_count" in metrics_text


def test_db_active_connections_gauge(client: TestClient) -> None:
    """AC 4: Verify DB active connections gauge is instantiated and exposed."""
    response = client.get("/metrics")
    assert "db_active_connections" in response.text
