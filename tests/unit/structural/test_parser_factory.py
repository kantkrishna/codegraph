# tests/unit/structural/test_parser_factory.py

# This file tests the routing logic of the Parser Factory.

from typing import Any

import pytest

from backend.models.events import FileDiscovered
from backend.services.parsers.factory import process_discovered_file


@pytest.mark.asyncio
async def test_factory_routes_python_file(mocker: Any) -> None:
    """Verify the factory correctly routes and publishes extracted events to the Event Bus."""

    # FIX: We now mock the ACTUAL Epic 3 Event Publisher, not the local mock function
    mock_event_bus = mocker.patch(
        "backend.services.parsers.factory._EVENT_BUS.publish", new_callable=mocker.AsyncMock
    )

    mocker.patch("backend.services.parsers.factory.os.path.exists", return_value=True)
    mocker.patch(
        "backend.services.parsers.factory.os.path.join", return_value="/tmp/fake_repo/main.py"
    )

    event = FileDiscovered(repository_id=1, file_path="main.py", language="py")
    source_code = b"class App:\n  pass"

    mocker.patch("builtins.open", mocker.mock_open(read_data=source_code))

    await process_discovered_file(event, "/tmp/fake_repo")

    # Assert the Event Bus was hit
    assert mock_event_bus.call_count >= 1

    # Verify the payload sent to the bus was correctly routed to the knowledge topic
    called_topic, called_payload = mock_event_bus.call_args[0]
    assert called_topic == "events.knowledge.extracted"
    assert b"App" in called_payload
    assert b"Class" in called_payload


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
