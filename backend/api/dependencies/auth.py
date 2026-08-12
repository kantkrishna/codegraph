# backend/api/dependencies/auth.py

# This file contains authentication dependencies, including GitHub webhook HMAC verification.

import hashlib
import hmac

from fastapi import HTTPException, Request

from backend.core.config import settings


def verify_github_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """Verifies the HMAC SHA-256 signature from GitHub webhooks."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    hash_object = hmac.new(secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


async def validate_github_webhook(request: Request) -> bytes:
    """FastAPI Dependency to validate incoming GitHub Webhooks."""
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    secret = settings.GITHUB_WEBHOOK_SECRET.get_secret_value()

    if not verify_github_signature(payload, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid GitHub Webhook Signature")

    return payload
