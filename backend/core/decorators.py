# backend/core/decorators.py

# This file provides robust resilience wrappers, specifically targeting Neo4j
# transient deadlocks that occur during concurrent ingestion events.

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from neo4j.exceptions import TransientError

F = TypeVar("F", bound=Callable[..., Any])


def with_neo4j_retries(max_retries: int = 3, base_delay: float = 0.5) -> Callable[[F], F]:
    """
    Decorator that applies exponential backoff for Neo4j TransientErrors.
    Crucial for handling concurrent MERGE deadlocks in asynchronous event consumers.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    retries += 1
                    if retries > max_retries:
                        raise e
                    # Exponential backoff: base_delay * 2^(retry-1)
                    time.sleep(base_delay * (2 ** (retries - 1)))

        return cast(F, wrapper)

    return decorator
