# backend/main.py

# This file defines the main FastAPI application instance.
import contextlib
from collections.abc import AsyncIterator

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from backend.api.middleware.logging_middleware import LoggingMiddleware
from backend.api.middleware.metrics_middleware import MetricsMiddleware

# Import the health router
from backend.api.routers import health, system, webhooks
from backend.core.config import settings
from backend.core.logger import setup_logging
from backend.core.telemetry import setup_telemetry

# Initialize structured logging before app startup
setup_logging()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: Initialize ARQ Redis pool and attach to app state
    app.state.redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    yield
    # Shutdown: Close Redis connection
    if hasattr(app.state, "redis"):
        await app.state.redis.close()


app = FastAPI(
    title="CodeGraph Enterprise Platform",
    description="Enterprise Developer Intelligence Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# Register Middlewares (Order matters: Logging wraps Metrics wraps Request)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

# Register Routers
app.include_router(system.router)
app.include_router(webhooks.router)

# Register the database-checking health router
app.include_router(health.router)

# Initialize OpenTelemetry for Distributed Tracing
setup_telemetry(app)