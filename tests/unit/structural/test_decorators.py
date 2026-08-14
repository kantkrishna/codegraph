# tests/unit/structural/test_decorators.py

# This file contains unit tests for backend resilience decorators, specifically
# testing exponential backoff for transient database errors.

from unittest.mock import MagicMock

import pytest
from neo4j.exceptions import TransientError

from backend.core.decorators import with_neo4j_retries


def test_retry_decorator_success_first_try() -> None:
    mock_func = MagicMock(return_value="success")
    decorated = with_neo4j_retries(max_retries=3, base_delay=0.01)(mock_func)

    assert decorated() == "success"
    assert mock_func.call_count == 1


def test_retry_decorator_transient_error_then_success() -> None:
    mock_func = MagicMock(side_effect=[TransientError("Deadlock"), "success"])
    decorated = with_neo4j_retries(max_retries=3, base_delay=0.01)(mock_func)

    assert decorated() == "success"
    assert mock_func.call_count == 2


def test_retry_decorator_max_retries_exceeded() -> None:
    mock_func = MagicMock(side_effect=TransientError("Deadlock"))
    decorated = with_neo4j_retries(max_retries=2, base_delay=0.01)(mock_func)

    with pytest.raises(TransientError):
        decorated()

    # Initial call + 2 retries = 3 calls
    assert mock_func.call_count == 3
