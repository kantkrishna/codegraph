# tests/unit/foundation/test_exceptions.py

# This test file is used to verify that the global exception handler in the FastAPI
# application correctly handles unhandled exceptions and returns a standardized JSON
# response.

from typing import Any

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from backend.api.main import app

error_router = APIRouter()


@error_router.get("/trigger-error")
def trigger_error() -> dict[str, Any]:
    raise ValueError("Simulated catastrophic failure")


app.include_router(error_router)


# Define the client as a proper Pytest fixture
@pytest.fixture
def client() -> TestClient:
    # Tell TestClient NOT to crash on 500 errors, so we can assert the JSON response
    return TestClient(app, raise_server_exceptions=False)


def test_global_exception_handler(client: TestClient) -> None:
    """Verify unhandled exceptions return a standardized 500 JSON response."""
    response = client.get("/trigger-error")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"] == "Internal Server Error"
    assert "Simulated catastrophic failure" in data["detail"]
