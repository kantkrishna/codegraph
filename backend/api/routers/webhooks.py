# backend/api/routers/webhooks.py
# This file exposes endpoints to receive events from external systems like GitHub.

import json
from typing import Any

from fastapi import APIRouter, Depends, Request

from backend.api.dependencies.auth import validate_github_webhook

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request, payload: bytes = Depends(validate_github_webhook)
) -> dict[str, str]:
    """Receives GitHub webhooks and enqueues ingestion tasks."""
    event_type = request.headers.get("X-GitHub-Event")
    data: dict[str, Any] = json.loads(payload)

    if event_type == "push":
        # Extract payload safely
        repo_data = data.get("repository", {})
        clone_url = repo_data.get("clone_url")
        repo_id = repo_data.get("id")
        ref = data.get("ref", "")

        if clone_url and repo_id:
            # Enqueue the background clone job via ARQ
            redis_pool = getattr(request.app.state, "redis", None)
            if redis_pool:
                await redis_pool.enqueue_job("clone_repository_task", clone_url, repo_id, ref)
                return {"status": "accepted", "message": "Ingestion enqueued"}

    return {"status": "ignored", "message": "Event not processed"}
