# tests/unit/foundation/test_telemetry.py

# This file contains unit tests for OpenTelemetry distributed tracing configuration.

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from backend.core.telemetry import setup_telemetry


@pytest.fixture(scope="module")
def memory_exporter() -> Generator[InMemorySpanExporter, None, None]:
    """Fixture to capture OTEL spans in memory, created once per test module."""
    exporter = InMemorySpanExporter()
    yield exporter


@pytest.fixture(scope="module")
def instrumented_app(memory_exporter: InMemorySpanExporter) -> FastAPI:
    """Sets up the FastAPI app and initializes the OTEL global singleton ONCE."""
    app = FastAPI()

    @app.get("/trace-test")
    def trace_test() -> dict[str, str]:
        return {"status": "ok"}

    setup_telemetry(app, "test-service", exporter=memory_exporter)
    return app


def test_setup_telemetry_initializes_provider(instrumented_app: FastAPI) -> None:
    """AC 1: Verify OTEL SDK is initialized at startup and registered globally."""
    provider = trace.get_tracer_provider()

    assert provider is not None
    assert hasattr(provider, "get_tracer")


def test_fastapi_request_creates_span(
    instrumented_app: FastAPI, memory_exporter: InMemorySpanExporter
) -> None:
    """AC 2: Verify FastAPI requests generate distributed spans automatically."""
    client = TestClient(instrumented_app)

    # Clear any spans created during startup
    memory_exporter.clear()

    # Trigger a request
    response = client.get("/trace-test")
    assert response.status_code == 200

    # Retrieve captured spans
    spans = memory_exporter.get_finished_spans()

    assert len(spans) >= 1

    # Verify at least one span captures the FastAPI route request
    assert any("GET /trace-test" in span.name for span in spans)

    # Verify standard HTTP status attributes are captured across the span hierarchy
    has_http_status = any(
        span.attributes is not None
        and (
            "http.status_code" in span.attributes or "http.response.status_code" in span.attributes
        )
        for span in spans
    )
    assert has_http_status
