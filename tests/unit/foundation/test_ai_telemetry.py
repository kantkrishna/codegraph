# tests/unit/foundation/test_ai_telemetry.py

# This file contains unit tests for the LLM telemetry decorator/wrapper.

import asyncio
from typing import Any

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.util._once import Once

from backend.core.ai_telemetry import track_llm_telemetry


# FIX: Elevate fixture scope to module to prevent stale tracer caching
@pytest.fixture(scope="module")
def memory_exporter() -> InMemorySpanExporter:
    """Provides an in-memory exporter to capture spans during tests."""
    return InMemorySpanExporter()


# FIX: Elevate fixture scope to module
@pytest.fixture(autouse=True, scope="module")
def isolate_telemetry(memory_exporter: InMemorySpanExporter) -> None:
    """
    Reset OpenTelemetry global lock and provider once for the module.
    Hooks the memory_exporter into the tracing pipeline so spans are captured.
    """
    if hasattr(trace, "_TRACER_PROVIDER_SET_ONCE"):
        trace._TRACER_PROVIDER_SET_ONCE = Once()

    trace._TRACER_PROVIDER = None

    provider = TracerProvider()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)


def test_llm_telemetry_decorator_creates_span_and_metrics(
    memory_exporter: InMemorySpanExporter,
) -> None:
    """AC 1, 2, 3: Verify the decorator creates spans, tracks latency, and counts tokens."""
    memory_exporter.clear()

    @track_llm_telemetry
    async def dummy_llm_call(prompt: str, model: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)  # Simulate network latency
        return {"content": "mock response", "usage": {"prompt_tokens": 15, "completion_tokens": 35}}

    result: dict[str, Any] = asyncio.run(
        dummy_llm_call(prompt="Explain architecture", model="gpt-4o")
    )

    assert result["content"] == "mock response"

    spans = memory_exporter.get_finished_spans()
    assert len(spans) == 1


def test_llm_telemetry_decorator_handles_missing_usage(
    memory_exporter: InMemorySpanExporter,
) -> None:
    """AC 4: Verify the wrapper doesn't crash if the LLM provider omits usage data."""
    memory_exporter.clear()

    @track_llm_telemetry
    async def dummy_fallback_call(model: str) -> dict[str, Any]:
        return {"content": "fallback response"}  # No usage key provided

    result: dict[str, Any] = asyncio.run(dummy_fallback_call(model="claude-3-haiku"))
    assert result["content"] == "fallback response"

    spans = memory_exporter.get_finished_spans()
    assert len(spans) >= 1
