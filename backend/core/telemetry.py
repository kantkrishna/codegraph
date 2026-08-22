# backend/core/telemetry.py

# This file configures OpenTelemetry for distributed tracing across the platform.

import os
import logging
from typing import Any
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter

logger = logging.getLogger(__name__)

def setup_telemetry(
    app: FastAPI | None = None, service_name: str = "codegraph-api", exporter: SpanExporter | None = None
) -> None:
    try:
        # 1. Create Resource and Provider unconditionally
        resource = Resource(attributes={SERVICE_NAME: service_name})
        sdk_provider = TracerProvider(resource=resource)
        
        # 2. Add Exporter
        if exporter is None:
            endpoint = os.getenv("OTLP_ENDPOINT", "http://jaeger:4318/v1/traces")
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            # Flush every 1000ms instead of 5000ms for rapid local observability
            processor: Any = BatchSpanProcessor(otlp_exporter, schedule_delay_millis=1000)
        else:
            processor = SimpleSpanProcessor(exporter)
            
        sdk_provider.add_span_processor(processor)
        trace.set_tracer_provider(sdk_provider)
        
        # 3. Instrument FastAPI explicitly if provided
        if app is not None:
            FastAPIInstrumentor().instrument_app(app, tracer_provider=sdk_provider)
            
        logger.info(f"OpenTelemetry successfully initialized for {service_name}")
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)

def instrument_db_engine(engine: Any) -> None:
    SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True, commenter_options={})