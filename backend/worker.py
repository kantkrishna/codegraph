# backend/worker.py

# This file configures the ARQ (Async Redis Queue) worker for background processing.

from typing import Any

from arq.connections import RedisSettings

from backend.core.config import settings
from backend.core.events.broker import event_broker
from backend.core.logger import setup_logging
from backend.services.git_service import clone_and_process_repository


async def clone_repository_task(
    ctx: dict[str, Any], clone_url: str, repo_id: int, branch: str
) -> None:
    """ARQ Task wrapper for repository cloning."""
    await clone_and_process_repository(clone_url, repo_id, branch)


# Define the startup hook
async def startup(ctx: dict[str, Any]) -> None:
    setup_logging()
    # Initialize the Kafka producer for the worker process
    await event_broker.connect()


# Ensure clean disconnection on worker termination
async def shutdown(ctx: dict[str, Any]) -> None:
    await event_broker.disconnect()


class WorkerSettings:
    """Configuration for the ARQ worker process."""

    functions = [clone_repository_task]
    # redis_settings = settings.REDIS_URL

    # Parse the URL string into an arq RedisSettings object
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    max_jobs = 10
    job_timeout = 600  # 10 minutes max for cloning massive repos

    on_startup = startup
    on_shutdown = shutdown


# To run the worker:
# `arq backend.worker.WorkerSettings`
