# tests/unit/structural/test_confluence_client.py

# Tests for US-5.3 AC1 & AC2 (API Integration & Filtering).

from unittest.mock import MagicMock, patch

import pytest

from etl.connectors.confluence.client import ConfluenceCloudClient


@pytest.mark.asyncio
async def test_fetch_pages_since() -> None:
    client = ConfluenceCloudClient("https://wiki.test", "user@test.com", "token123")

    with patch("httpx.AsyncClient.get") as mock_get:
        # The HTTPX response object methods (like json() and raise_for_status())
        # are synchronous, so we use MagicMock instead of AsyncMock.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"id": "1", "title": "Setup", "body": {"view": {"value": "<p>Hi</p>"}}}]
        }
        mock_get.return_value = mock_response

        pages = await client.fetch_pages_since("2026-01-01T00:00:00Z")

        assert len(pages) == 1
        assert pages[0]["title"] == "Setup"
        assert pages[0]["body"] == "<p>Hi</p>"
        mock_get.assert_called_once()
        # Verify CQL filter was applied in the URL
        assert "lastModified" in str(mock_get.call_args)
