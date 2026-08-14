# backend/worker.py

# This file configures the ARQ (Async Redis Queue) worker for background processing.

from typing import Any

from arq.connections import RedisSettings

from backend.core.config import settings
from backend.services.git_service import clone_and_process_repository


async def clone_repository_task(
    ctx: dict[str, Any], clone_url: str, repo_id: int, branch: str
) -> None:
    """ARQ Task wrapper for repository cloning."""
    await clone_and_process_repository(clone_url, repo_id, branch)


class WorkerSettings:
    """Configuration for the ARQ worker process."""

    functions = [clone_repository_task]
    # redis_settings = settings.REDIS_URL

    # Parse the URL string into an arq RedisSettings object
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    max_jobs = 10
    job_timeout = 600  # 10 minutes max for cloning massive repos


# To run the worker:
# `arq backend.worker.WorkerSettings`
