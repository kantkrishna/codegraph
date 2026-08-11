# tests/unit/foundation/test_ai_telemetry.py
#
# This file contains unit tests for the LLM telemetry decorator/wrapper.

import asyncio
from collections.abc import Generator
from typing import Any

import pytest
from fastapi import FastAPI
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from prometheus_client import generate_latest

from backend.core.ai_telemetry import track_llm_telemetry
from backend.core.telemetry import setup_telemetry


# CRITICAL: scope="module" ensures this only runs ONCE for the whole file
@pytest.fixture(scope="module")
def memory_exporter() -> Generator[InMemorySpanExporter, None, None]:
    """Fixture to capture OTEL spans in memory, hooked into the global telemetry safely."""
    exporter = InMemorySpanExporter()
    setup_telemetry(FastAPI(), "ai-test", exporter=exporter)
    yield exporter


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
    span = spans[0]
    assert span.name == "llm_generation"
    assert span.attributes is not None
    assert span.attributes["llm.model"] == "gpt-4o"
    assert span.attributes["llm.usage.prompt_tokens"] == 15
    assert span.attributes["llm.usage.completion_tokens"] == 35

    metrics_text = generate_latest().decode("utf-8")
    assert "llm_tokens_total" in metrics_text
    assert 'model="gpt-4o"' in metrics_text
    assert 'token_type="prompt"' in metrics_text
    assert 'token_type="completion"' in metrics_text
    assert "llm_generation_duration_seconds_bucket" in metrics_text


def test_llm_telemetry_decorator_handles_missing_usage(
    memory_exporter: InMemorySpanExporter,
) -> None:
    """AC 4: Verify the wrapper doesn't crash if the LLM provider omits usage data."""
    # Clear the exporter memory from the first test
    memory_exporter.clear()

    @track_llm_telemetry
    async def dummy_fallback_call(model: str) -> dict[str, Any]:
        return {"content": "fallback response"}  # No usage key provided

    result: dict[str, Any] = asyncio.run(dummy_fallback_call(model="claude-3-haiku"))
    assert result["content"] == "fallback response"

    spans = memory_exporter.get_finished_spans()
    assert len(spans) >= 1
    assert spans[0].attributes is not None
    assert spans[0].attributes["llm.model"] == "claude-3-haiku"
    assert spans[0].attributes.get("llm.usage.prompt_tokens") == 0
