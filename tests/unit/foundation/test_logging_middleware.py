# tests/unit/foundation/test_logging_middleware.py

# This file contains integration tests for the FastAPI logging middleware.

from io import StringIO

import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.middleware.logging_middleware import LoggingMiddleware
from backend.core.logger import setup_logging

app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.get("/test-endpoint")
async def dummy_endpoint() -> dict[str, str]:
    # AC 1: Log request
    logger = structlog.get_logger("dummy_endpoint")
    logger.info("processing_request")
    return {"status": "ok"}


client = TestClient(app)


def test_middleware_injects_request_id() -> None:
    """AC 2: Verify a unique request_id is injected into the response headers."""
    response = client.get("/test-endpoint")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_propagates_to_logs() -> None:
    """AC 3: Verify the request_id is automatically propagated to structlog context."""
    # Create an explicit in-memory stream
    stream = StringIO()

    # Bind the logger to our explicit stream instead of sys.stdout
    setup_logging(stream=stream)

    response = client.get("/test-endpoint")

    request_id = response.headers["X-Request-ID"]

    # Read directly from our stream buffer
    log_output = stream.getvalue()

    # Check that the request_id made its way into the JSON log output
    assert request_id in log_output
    assert f'"request_id": "{request_id}"' in log_output
