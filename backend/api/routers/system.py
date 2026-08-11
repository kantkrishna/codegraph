# backend/api/routers/system.py
#
# This file defines system-level endpoints such as health checks and metrics.

from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

router = APIRouter(tags=["System"])


@router.get("/metrics")
async def get_metrics() -> Response:
    """AC 1: Expose Prometheus metrics in the standard text format."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
