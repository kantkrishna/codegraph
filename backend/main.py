# backend/main.py

# This file defines the main FastAPI application instance.

from fastapi import FastAPI

from backend.api.middleware.logging_middleware import LoggingMiddleware
from backend.core.logger import setup_logging
from backend.core.telemetry import setup_telemetry

# Initialize structured logging before app startup
setup_logging()

app = FastAPI(
    title="CodeGraph Enterprise Platform",
    description="Enterprise Developer Intelligence Platform API",
    version="0.1.0",
)

# Register Middleware
app.add_middleware(LoggingMiddleware)

# AC 1: Initialize OpenTelemetry for Distributed Tracing
setup_telemetry(app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
