# backend/core/telemetry.py

# This file configures OpenTelemetry for distributed tracing across the platform.

from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter


def setup_telemetry(
    app: FastAPI, service_name: str = "codegraph-api", exporter: SpanExporter | None = None
) -> None:
    """Initializes OpenTelemetry tracing and instruments the FastAPI app (AC 1 & 2)."""
    current_provider = trace.get_tracer_provider()

    # Idempotency: If it's already an active SDK provider, just append the exporter
    if hasattr(current_provider, "add_span_processor"):
        if exporter is not None:
            current_provider.add_span_processor(SimpleSpanProcessor(exporter))
        try:
            FastAPIInstrumentor().instrument_app(app)
        except Exception:
            pass
        return

    resource = Resource(attributes={SERVICE_NAME: service_name})
    sdk_provider = TracerProvider(resource=resource)

    if exporter is None:
        # Production/Local Docker route: OTLP exporter pushing to Jaeger (AC 4)
        otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
        processor: Any = BatchSpanProcessor(otlp_exporter)
    else:
        # Testing route: pushes spans to memory sequentially
        processor = SimpleSpanProcessor(exporter)

    sdk_provider.add_span_processor(processor)

    # FORCE override the global provider to bypass NoOp locks and warnings during testing
    setattr(trace, "_TRACER_PROVIDER", sdk_provider)

    try:
        # AC 2: Instrument FastAPI to capture all incoming HTTP requests
        FastAPIInstrumentor().instrument_app(app)
    except Exception:
        pass


def instrument_db_engine(engine: Any) -> None:
    """AC 3: Helper to instrument SQLAlchemy engines once initialized."""
    SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True, commenter_options={})
