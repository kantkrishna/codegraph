# backend/api/exceptions.py

# This file defines a global exception handler for the FastAPI application. It catches
# all unhandled exceptions and returns a standardized JSON response with a 500 status
# code.

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unhandled exceptions and returns a strict JSON format."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )
