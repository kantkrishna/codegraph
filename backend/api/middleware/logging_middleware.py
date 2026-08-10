# backend/api/middleware/logging_middleware.py

# This file defines the FastAPI middleware that tracks request lifecycles.

import uuid
from typing import Any

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # AC 2: Generate unique request_id
        request_id = str(uuid.uuid4())

        # AC 3: Bind request_id to the structlog context variables for this asyncio task
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        # Mask authorization header if logging incoming headers directly (AC 4)
        logger = structlog.get_logger("api.request")
        logger.info("http_request_started")

        response = await call_next(request)

        # Inject into response header
        response.headers["X-Request-ID"] = request_id

        logger.info("http_request_completed", status_code=response.status_code)

        return response
