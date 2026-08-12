# tests/unit/foundation/test_db.py

# This file contains unit tests for the database dependency injection.

from collections.abc import Generator
from typing import Any

import pytest

from backend.infrastructure.db import get_db


def test_get_db_yields_session_and_closes(mocker: Any) -> None:
    """Verify that the database dependency yields a session and closes it cleanly."""
    # Mock the SQLAlchemy SessionLocal factory
    mock_session_local = mocker.patch("backend.infrastructure.db.SessionLocal")
    mock_session_instance = mock_session_local.return_value

    # Execute the generator
    db_generator = get_db()

    # The first next() should yield the session
    yielded_session = next(db_generator)
    assert yielded_session == mock_session_instance

    # The generator should close the session upon completion
    with pytest.raises(StopIteration):
        next(db_generator)

    mock_session_instance.close.assert_called_once()


def test_get_db_closes_session_on_exception(mocker: Any) -> None:
    """Verify that if an API route crashes, the DB session is still closed."""
    mock_session_local = mocker.patch("backend.infrastructure.db.SessionLocal")
    mock_session_instance = mock_session_local.return_value

    db_generator = get_db()
    next(db_generator)  # Yield the session

    # Simulate a crash in the FastAPI route
    with pytest.raises(RuntimeError, match="Route crashed"):
        try:
            raise RuntimeError("Route crashed")
        finally:
            # FastAPI's Depends() will trigger the finally block of the generator
            # db_generator.close()
            Generator.close(db_generator)

    # Ensure the connection didn't leak
    mock_session_instance.close.assert_called_once()
