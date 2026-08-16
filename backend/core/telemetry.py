# backend/core/telemetry.py

# This file configures OpenTelemetry for distributed tracing across the platform.

import os
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter
from opentelemetry.util._once import Once


def setup_telemetry(
    app: FastAPI, service_name: str = "codegraph-api", exporter: SpanExporter | None = None
) -> None:
    """Initializes OpenTelemetry tracing and instruments the FastAPI app (AC 1 & 2)."""

    # --- THE RESTORED IDEMPOTENCY BLOCK ---
    current_provider = trace.get_tracer_provider()

    if hasattr(current_provider, "add_span_processor"):
        if exporter is not None:
            current_provider.add_span_processor(SimpleSpanProcessor(exporter))
        try:
            FastAPIInstrumentor().instrument_app(app)
        except Exception:
            pass
        return
    # --------------------------------------

    # 1. Create a new TracerProvider for the service
    resource = Resource(attributes={SERVICE_NAME: service_name})
    sdk_provider = TracerProvider(resource=resource)

    if exporter is None:
        # Production/Local Docker route: OTLP exporter pushing to Jaeger
        endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        processor: Any = BatchSpanProcessor(otlp_exporter)
    else:
        # Testing route: pushes spans to memory sequentially
        processor = SimpleSpanProcessor(exporter)

    sdk_provider.add_span_processor(processor)

    # 2. Reset OTEL lock to allow overriding the provider during Pytest runs
    if hasattr(trace, "_TRACER_PROVIDER_SET_ONCE"):
        trace._TRACER_PROVIDER_SET_ONCE = Once()

    # 3. Safely set global provider so ProxyTracers correctly route to it
    trace.set_tracer_provider(sdk_provider)

    # 4. Instrument the app securely
    try:
        # Uninstrument first to prevent Duplicate Instrumentation warnings in Pytest
        FastAPIInstrumentor().uninstrument_app(app)
    except Exception:
        pass

    try:
        # Re-instrument with the newly attached provider
        FastAPIInstrumentor().instrument_app(app)
    except Exception:
        pass


def instrument_db_engine(engine: Any) -> None:
    """AC 3: Helper to instrument SQLAlchemy engines once initialized."""
    SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True, commenter_options={})
