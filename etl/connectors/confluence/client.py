# etl/connectors/confluence/client.py

# Async HTTP client wrapper specific to Atlassian Confluence Cloud API (US-5.3).

from typing import Any

import httpx


class ConfluenceCloudClient:
    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = (email, api_token)

    async def fetch_pages_since(self, iso_timestamp: str) -> list[dict[str, Any]]:
        """Queries the Confluence v2 API for pages modified since a timestamp."""
        url = f"{self.base_url}/wiki/api/v2/pages"
        # CQL to enforce incremental fetch
        params = {"cql": f"lastModified >= '{iso_timestamp}'", "body-format": "view"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            data = response.json()

            results: list[dict[str, Any]] = []
            for item in data.get("results", []):
                results.append(
                    {
                        "id": str(item.get("id")),
                        "title": str(item.get("title")),
                        "body": str(item.get("body", {}).get("view", {}).get("value", "")),
                        "url": f"{self.base_url}/wiki{item.get('_links', {}).get('webui', '')}",
                    }
                )
            return results
