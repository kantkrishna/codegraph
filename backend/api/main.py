# backend/api/main.py

# This file defines the main FastAPI application instance. It sets up the application,
# registers routers, and configures global exception handling.

from fastapi import FastAPI

from backend.api.exceptions import global_exception_handler
from backend.api.routers import health
from backend.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # Register exception handlers
    app.add_exception_handler(Exception, global_exception_handler)

    # Register routers
    app.include_router(health.router, tags=["Platform Health"])

    return app


app = create_app()
