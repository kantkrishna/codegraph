# backend/services/github_auth.py

# This file handles secure authentication as a GitHub App installation.

import time

import jwt

from backend.core.config import settings


def generate_github_app_jwt() -> str:
    """
    Generates a short-lived JWT to authenticate as the GitHub App.
    Used to dynamically fetch Installation Access Tokens for cloning.
    """
    app_id = settings.GITHUB_APP_ID
    private_key = None
    if settings.GITHUB_PRIVATE_KEY:
        private_key = settings.GITHUB_PRIVATE_KEY.get_secret_value()

    if not app_id or not private_key:
        raise ValueError(
            "GitHub App credentials are not fully configured in environment variables."
        )

    now = int(time.time())
    payload = {
        "iat": now - 60,  # Issued at time (60 seconds in the past for clock drift)
        "exp": now + (10 * 60),  # Expiration time (Maximum 10 minutes)
        "iss": app_id,  # GitHub App ID
    }

    # Generate the JWT using RS256 as required by GitHub API
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt
