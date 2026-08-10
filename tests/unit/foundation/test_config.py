# tests/unit/foundation/test_config.py

# This test file is used to verify that the Pydantic settings load correctly from
# environment variables or defaults.

from backend.core.config import settings


def test_config_loads_correctly() -> None:
    """Verify Pydantic settings load environment variables or defaults."""
    assert settings.PROJECT_NAME == "CodeGraph API"
    assert "bolt://" in settings.NEO4J_URI
    assert "postgresql://" in settings.DATABASE_URL
