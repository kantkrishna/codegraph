# backend/core/ai_telemetry.py
#
# This file defines observability wrappers for tracking LLM token usage and latency.

import time
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from opentelemetry import trace

from backend.core.metrics import LLM_GENERATION_DURATION_SECONDS, LLM_TOKENS_TOTAL

tracer = trace.get_tracer(__name__)


# Use modern Python 3.12+ PEP 695 generic syntax
def track_llm_telemetry[**P, R: dict[str, Any]](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
    """
    Async decorator that wraps AI calls to record OpenTelemetry spans
    and Prometheus metrics for token usage and model latency.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Extract model from kwargs if available, default to "unknown"
        model = str(kwargs.get("model", "unknown"))
        start_time = time.time()

        # AC 1: Create a specialized LLM span
        with tracer.start_as_current_span("llm_generation") as span:
            span.set_attribute("llm.model", model)

            try:
                response = await func(*args, **kwargs)

                # AC 4: Safely extract usage data if it exists in the response
                usage = response.get("usage", {})
                if isinstance(usage, dict):
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)

                    # AC 2: Track tokens in Prometheus
                    LLM_TOKENS_TOTAL.labels(model=model, token_type="prompt").inc(prompt_tokens)

                    LLM_TOKENS_TOTAL.labels(model=model, token_type="completion").inc(
                        completion_tokens
                    )

                    # Attach token metrics to the distributed trace
                    span.set_attribute("llm.usage.prompt_tokens", prompt_tokens)
                    span.set_attribute("llm.usage.completion_tokens", completion_tokens)

                return response
            finally:
                duration = time.time() - start_time
                # AC 3: Observe latency in Prometheus
                LLM_GENERATION_DURATION_SECONDS.labels(model=model).observe(duration)

    return wrapper
