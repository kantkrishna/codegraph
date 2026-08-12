# backend/core/config.py

# This file defines the Pydantic settings for the application, which are loaded from
# environment variables or defaults.

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Neo4j Configuration
    PROJECT_NAME: str = "CodeGraph API"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "codegraph_secret"
    DATABASE_URL: str = "postgresql://postgres:codegraph_secret@localhost:5432/codegraph"

    # GitHub App Integration
    GITHUB_APP_ID: str | None = None
    GITHUB_PRIVATE_KEY: SecretStr | None = None
    GITHUB_WEBHOOK_SECRET: SecretStr = SecretStr("")

    # Redis Worker
    REDIS_URL: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
