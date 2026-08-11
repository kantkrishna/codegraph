# backend/api/middleware/metrics_middleware.py
#
# This file defines the FastAPI middleware for tracking HTTP Prometheus metrics.

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        method = request.method
        path = request.url.path

        start_time = time.time()
        status_code = "500"

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        finally:
            duration = time.time() - start_time
            # Increment Counter
            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
            # Observe Latency Histogram
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)
