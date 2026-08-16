# tests/unit/structural/test_parser_factory.py

# This file tests the routing logic of the Parser Factory.

from typing import Any

import pytest

from backend.models.events import EntityExtracted, FileDiscovered
from backend.services.parsers.factory import process_discovered_file


@pytest.mark.asyncio
async def test_factory_routes_python_file(mocker: Any) -> None:
    """Verify the factory correctly routes and publishes extracted events."""
    mock_publish = mocker.patch(
        "backend.services.parsers.factory.publish_event", new_callable=mocker.AsyncMock
    )

    # Mock the OS safety check so the factory proceeds to parsing
    mocker.patch("os.path.exists", return_value=True)

    # FIX: Explicitly mock the PythonParser so we test routing isolation, not Tree-sitter
    mock_parser = mocker.patch("backend.services.parsers.factory._PY_PARSER.parse")
    mock_parser.return_value = (
        [EntityExtracted(repository_id=1, file_path="main.py", entity_type="Class", name="App")],
        [],  # No relationships for this mock
    )

    event = FileDiscovered(repository_id=1, file_path="main.py", language="py")
    source_code = b"class App:\n  pass"

    # Mock file reading
    mocker.patch("builtins.open", mocker.mock_open(read_data=source_code))

    await process_discovered_file(event, "/tmp/fake_repo")

    # Ensure publish_event was successfully triggered
    mock_publish.assert_called_once()


@pytest.mark.asyncio
async def test_factory_handles_exception(mocker: Any) -> None:
    """Verify the factory ignores malformed files without crashing (boosts coverage)."""
    mocker.patch("backend.services.parsers.factory.os.path.exists", return_value=True)
    mocker.patch(
        "backend.services.parsers.factory.os.path.join", return_value="/tmp/fake_repo/broken.py"
    )

    # Simulate a corrupted disk read
    mocker.patch("builtins.open", side_effect=Exception("Simulated Read Error"))

    event = FileDiscovered(repository_id=1, file_path="broken.py", language="py")

    # Should safely swallow the exception and not crash
    await process_discovered_file(event, "/tmp/fake_repo")
