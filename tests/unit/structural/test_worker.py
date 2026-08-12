# tests/unit/structural/test_worker.py

# This file contains unit tests for the ARQ (Asynchronous Redis Queue) worker.

from typing import Any

import pytest

from backend.core.config import settings
from backend.worker import WorkerSettings, clone_repository_task


@pytest.mark.asyncio
async def test_clone_repository_task_delegates_to_service(mocker: Any) -> None:
    """Verify that the ARQ task wrapper correctly calls the underlying git service."""
    # Mock the underlying service that the worker calls
    mock_clone_service = mocker.patch("backend.worker.clone_and_process_repository")

    # Simulate the ARQ context dictionary
    mock_ctx = {"redis": mocker.MagicMock()}

    test_url = "https://github.com/enterprise/repo.git"
    test_id = 456
    test_branch = "main"

    # Execute the worker task
    await clone_repository_task(mock_ctx, test_url, test_id, test_branch)

    # Assert delegation occurred with exact parameters
    mock_clone_service.assert_called_once_with(test_url, test_id, test_branch)


def test_worker_settings_configuration() -> None:
    """Verify the ARQ worker is configured with the correct functions and redis URL."""
    # Ensure the task we want to run is actually registered in the worker
    assert clone_repository_task in WorkerSettings.functions

    # Ensure it's pointing to the application's configured Redis instance
    assert WorkerSettings.redis_settings == settings.REDIS_URL

    # Ensure sensible defaults for massive git clones
    assert WorkerSettings.max_jobs > 0
    assert WorkerSettings.job_timeout >= 600
