# tests/unit/foundation/test_telemetry.py

# Comprehensive test suite to ensure 100% coverage for OpenTelemetry utilities,
# verifying idempotency logic, and exception safety boundaries.
# (Note: AI Telemetry decorator tests are handled in test_ai_telemetry.py)

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from opentelemetry.sdk.trace.export import SpanExporter

from backend.core.telemetry import (
    instrument_db_engine,
    setup_telemetry,
)


def test_setup_telemetry_idempotent_no_exporter() -> None:
    """
    Test that setup exits early if a provider is already active, without adding
    processors if no exporter is provided.
    """
    app = FastAPI()
    with (
        patch("backend.core.telemetry.trace.get_tracer_provider") as mock_get_provider,
        patch("backend.core.telemetry.FastAPIInstrumentor") as mock_fastapi_inst,
    ):
        mock_provider = MagicMock()
        # Simulating an active SDK provider that already has 'add_span_processor'
        mock_provider.add_span_processor = MagicMock()
        mock_get_provider.return_value = mock_provider

        setup_telemetry(app)

        mock_provider.add_span_processor.assert_not_called()
        mock_fastapi_inst.return_value.instrument_app.assert_called_once_with(app)


def test_setup_telemetry_idempotent_with_exporter_and_exception() -> None:
    """
    Test that an exporter is attached to an existing provider, and FastAPI instrument
    exceptions are swallowed safely.
    """
    app = FastAPI()
    exporter = MagicMock(spec=SpanExporter)
    with (
        patch("backend.core.telemetry.trace.get_tracer_provider") as mock_get_provider,
        patch("backend.core.telemetry.FastAPIInstrumentor") as mock_fastapi_inst,
    ):
        mock_provider = MagicMock()
        mock_provider.add_span_processor = MagicMock()
        mock_get_provider.return_value = mock_provider

        # Force exception in the try/except block to test safe passing
        mock_fastapi_inst.return_value.instrument_app.side_effect = Exception(
            "Simulated FastAPI Error"
        )

        setup_telemetry(app, exporter=exporter)

        mock_provider.add_span_processor.assert_called_once()
        mock_fastapi_inst.return_value.instrument_app.assert_called_once_with(app)


def test_setup_telemetry_fresh_provider_no_exporter() -> None:
    """Test standard production routing establishing an OTLP exporter and Batch processor."""
    app = FastAPI()
    with (
        patch("backend.core.telemetry.trace.get_tracer_provider") as mock_get_provider,
        patch("backend.core.telemetry.TracerProvider") as mock_tracer_provider,
        patch("backend.core.telemetry.OTLPSpanExporter") as mock_otlp,
        patch("backend.core.telemetry.BatchSpanProcessor") as mock_batch,
        patch("backend.core.telemetry.FastAPIInstrumentor") as mock_fastapi_inst,
        patch("backend.core.telemetry.setattr"),
    ):
        # Missing 'add_span_processor' simulates a fresh/default NoOp provider
        mock_get_provider.return_value = object()

        setup_telemetry(app)

        mock_otlp.assert_called_once()
        mock_batch.assert_called_once()
        mock_tracer_provider.return_value.add_span_processor.assert_called_once()
        mock_fastapi_inst.return_value.instrument_app.assert_called_once_with(app)


def test_setup_telemetry_fresh_provider_with_exporter_and_exception() -> None:
    """
    Test test routing establishing a Simple processor and handling trailing exceptions cleanly.
    """
    app = FastAPI()
    exporter = MagicMock(spec=SpanExporter)
    with (
        patch("backend.core.telemetry.trace.get_tracer_provider") as mock_get_provider,
        patch("backend.core.telemetry.TracerProvider") as mock_tracer_provider,
        patch("backend.core.telemetry.SimpleSpanProcessor") as mock_simple,
        patch("backend.core.telemetry.FastAPIInstrumentor") as mock_fastapi_inst,
        patch("backend.core.telemetry.setattr"),
    ):
        mock_get_provider.return_value = object()

        # Wrapped to comply with 100-character line limit
        mock_fastapi_inst.return_value.instrument_app.side_effect = Exception(
            "Simulated FastAPI Error"
        )

        setup_telemetry(app, exporter=exporter)

        mock_simple.assert_called_once_with(exporter)
        mock_tracer_provider.return_value.add_span_processor.assert_called_once()
        mock_fastapi_inst.return_value.instrument_app.assert_called_once_with(app)


def test_instrument_db_engine_success() -> None:
    """Test successful injection of SQLAlchemy telemetry."""
    engine = MagicMock()
    with patch("backend.core.telemetry.SQLAlchemyInstrumentor") as mock_sql_inst:
        instrument_db_engine(engine)
        mock_sql_inst.return_value.instrument.assert_called_once_with(
            engine=engine, enable_commenter=True, commenter_options={}
        )


def test_instrument_db_engine_exception() -> None:
    """Test that SQLAlchemy telemetry injection failures bubble up appropriately."""
    engine = MagicMock()
    with patch("backend.core.telemetry.SQLAlchemyInstrumentor") as mock_sql_inst:
        mock_sql_inst.return_value.instrument.side_effect = Exception("Simulated DB Engine Error")

        # Expect the exception to surface since there is no try/except in the source
        with pytest.raises(Exception, match="Simulated DB Engine Error"):
            instrument_db_engine(engine)

        mock_sql_inst.return_value.instrument.assert_called_once_with(
            engine=engine, enable_commenter=True, commenter_options={}
        )
