# tests/unit/structural/test_webhooks.py

# This file contains unit tests for the GitHub webhook router and HMAC signature validation.

import hashlib
import hmac
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.api.dependencies.auth import verify_github_signature
from backend.main import app

client = TestClient(app)


def test_verify_github_signature_valid() -> None:
    """Test that a valid HMAC signature returns True."""
    secret = "test_secret"
    payload = b'{"action": "created"}'
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_github_signature(payload, signature, secret) is True


def test_verify_github_signature_invalid() -> None:
    """Test that an invalid HMAC signature returns False."""
    assert (
        verify_github_signature(b'{"action": "created"}', "sha256=invalid", "test_secret") is False
    )


def test_webhook_endpoint_rejects_unauthorized() -> None:
    """Test that the webhook endpoint returns 401 for invalid signatures."""
    response = client.post(
        "/api/v1/webhooks/github",
        content=b'{"action": "push"}',
        headers={"X-Hub-Signature-256": "sha256=invalid"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_endpoint_accepts_and_enqueues(mocker: Any) -> None:
    """Test that valid webhooks are accepted and tasks are enqueued."""
    # Mock the ARQ redis pool on the app state
    mock_redis = mocker.AsyncMock()
    app.state.redis = mock_redis

    secret = "test_secret"
    # Temporarily override settings for test
    mocker.patch(
        "backend.api.dependencies.auth.settings.GITHUB_WEBHOOK_SECRET.get_secret_value",
        return_value=secret,
    )

    payload_dict = {
        "ref": "refs/heads/main",
        "repository": {"clone_url": "https://github.com/test/repo.git", "id": 123},
    }
    payload_bytes = json.dumps(payload_dict).encode()
    signature = "sha256=" + hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/webhooks/github",
        content=payload_bytes,
        headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": "push"},
    )

    assert response.status_code == 202
    mock_redis.enqueue_job.assert_called_once_with(
        "clone_repository_task", "https://github.com/test/repo.git", 123, "refs/heads/main"
    )
