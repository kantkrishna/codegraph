# tests/unit/structural/test_github_auth.py

# This file tests the ephemeral JWT generation for GitHub App authentication.

from typing import Any

import pytest

from backend.services.github_auth import generate_github_app_jwt


def test_generate_github_app_jwt_creates_valid_token(mocker: Any) -> None:
    """Verify that the JWT is correctly formed with exact 10-minute expirations."""
    # Mock the Pydantic settings
    mocker.patch("backend.services.github_auth.settings.GITHUB_APP_ID", "123456")

    mock_secret = mocker.patch("backend.services.github_auth.settings.GITHUB_PRIVATE_KEY")
    mock_secret.get_secret_value.return_value = (
        "-----BEGIN RSA PRIVATE KEY-----\nMOCK_KEY\n-----END RSA PRIVATE KEY-----"  # noqa: E501
    )

    # Mock jwt.encode to intercept payload validation
    mock_encode = mocker.patch(
        "backend.services.github_auth.jwt.encode", return_value="mock.jwt.token"
    )

    token = generate_github_app_jwt()

    assert token == "mock.jwt.token"
    mock_encode.assert_called_once()

    payload = mock_encode.call_args[0][0]
    assert payload["iss"] == "123456"
    assert "iat" in payload
    assert "exp" in payload
    # GitHub requires exp to be exactly 10 minutes after iat + 60s clock drift buffer
    assert payload["exp"] == payload["iat"] + (10 * 60) + 60


def test_generate_github_app_jwt_missing_config(mocker: Any) -> None:
    """Verify the service fails fast if secrets are missing."""
    mocker.patch("backend.services.github_auth.settings.GITHUB_APP_ID", None)
    with pytest.raises(ValueError, match="GitHub App credentials"):
        generate_github_app_jwt()
