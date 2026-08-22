# backend/worker.py

# This file configures the ARQ (Async Redis Queue) worker for background processing.

from typing import Any

from arq.connections import RedisSettings
from opentelemetry import trace

from backend.core.config import settings
from backend.core.events.broker import event_broker
from backend.core.logger import setup_logging
from backend.core.telemetry import setup_telemetry
from backend.services.git_service import clone_and_process_repository

tracer = trace.get_tracer(__name__)

async def clone_repository_task(
    ctx: dict[str, Any], clone_url: str, repo_id: int, branch: str
) -> None:
    """ARQ Task wrapper for repository cloning."""
    # Get tracer inside the task to avoid disconnected ProxyTracers
    tracer = trace.get_tracer(__name__)
    # Create a manual root span so Jaeger can track the ingestion pipeline
    with tracer.start_as_current_span("clone_repository_task") as span:
        span.set_attribute("repository.url", clone_url)
        await clone_and_process_repository(clone_url, repo_id, branch)

    # Force flush to Jaeger before the async task yields context
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()


# Define the startup hook
async def startup(ctx: dict[str, Any]) -> None:
    setup_logging()
    # Initialize OpenTelemetry for the worker process
    setup_telemetry(app=None, service_name="codegraph-worker")
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
