# backend/api/routers/health.py

# This file defines the health check endpoint for the FastAPI application. It checks
# the connectivity of the Neo4j and PostgreSQL databases and returns a JSON response
# indicating the status of the application and its dependencies.

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.infrastructure.db import verify_neo4j_connection, verify_postgres_connection

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, Any]:
    neo4j_ok = verify_neo4j_connection()
    pg_ok = verify_postgres_connection()

    status = "ok" if neo4j_ok and pg_ok else "error"

    response = {
        "status": status,
        "databases": {
            "neo4j": "connected" if neo4j_ok else "disconnected",
            "postgres": "connected" if pg_ok else "disconnected",
        },
    }

    if status == "error":
        raise HTTPException(status_code=503, detail=response)

    return response
