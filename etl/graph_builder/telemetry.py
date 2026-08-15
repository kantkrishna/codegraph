# etl/graph_builder/telemetry.py

# This file provides OpenTelemetry span decorators specifically for Graph writes.

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from opentelemetry import trace

tracer = trace.get_tracer(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def with_graph_telemetry(span_name: str) -> Callable[[F], F]:
    """Wraps consumer methods with OpenTelemetry spans for tracing DB writes."""

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(span_name) as span:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    span.record_exception(e)
                    raise

        return cast(F, wrapper)

    return decorator
