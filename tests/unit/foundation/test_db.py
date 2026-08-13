# tests/unit/foundation/test_db.py

# This file contains unit tests for the database infrastructure utilities,
# ensuring connection verifications handle successes and failures gracefully,
# and that the session generator cleans up connections correctly.

from unittest.mock import MagicMock, patch

import pytest

from backend.infrastructure.db import (
    get_db,
    verify_neo4j_connection,
    verify_postgres_connection,
)


@patch("backend.infrastructure.db.neo4j_driver.verify_connectivity")
def test_verify_neo4j_connection_success(mock_verify_connectivity: MagicMock) -> None:
    """Test that Neo4j verification returns True when no exception is raised."""
    mock_verify_connectivity.return_value = None

    result = verify_neo4j_connection()

    assert result is True
    mock_verify_connectivity.assert_called_once()


@patch("backend.infrastructure.db.neo4j_driver.verify_connectivity")
def test_verify_neo4j_connection_failure(mock_verify_connectivity: MagicMock) -> None:
    """Test that Neo4j verification returns False when an exception occurs."""
    mock_verify_connectivity.side_effect = Exception("Neo4j connection refused")

    result = verify_neo4j_connection()

    assert result is False
    mock_verify_connectivity.assert_called_once()


@patch("backend.infrastructure.db.psycopg2.connect")
def test_verify_postgres_connection_success(mock_connect: MagicMock) -> None:
    """Test that PostgreSQL verification returns True and closes the test connection."""
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection

    result = verify_postgres_connection()

    assert result is True
    mock_connect.assert_called_once()
    mock_connection.close.assert_called_once()


@patch("backend.infrastructure.db.psycopg2.connect")
def test_verify_postgres_connection_failure(mock_connect: MagicMock) -> None:
    """Test that PostgreSQL verification returns False when connection fails."""
    mock_connect.side_effect = Exception("PostgreSQL role does not exist")

    result = verify_postgres_connection()

    assert result is False
    mock_connect.assert_called_once()


@patch("backend.infrastructure.db.SessionLocal")
def test_get_db_yields_session_and_closes(mock_session_local: MagicMock) -> None:
    """
    Test that the get_db generator yields a session and closes it securely in the finally block.
    """
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Initialize the generator
    db_generator = get_db()

    # Act: Retrieve the session (simulating FastAPI injecting the dependency)
    session = next(db_generator)

    # Assert: Session is yielded, but not yet closed
    assert session == mock_session
    mock_session.close.assert_not_called()

    # Act: Exhaust the generator (simulating FastAPI tearing down the dependency after the request)
    with pytest.raises(StopIteration):
        next(db_generator)

    # Assert: The finally block executed and closed the session
    mock_session.close.assert_called_once()
