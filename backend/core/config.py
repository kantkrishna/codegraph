# backend/core/config.py

# This file defines the Pydantic settings for the application, which are loaded from
# environment variables or defaults.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeGraph API"
    NEO4J_URI: str = "bolt://localhost:7687"  # Localhost default for local testing
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "codegraph_secret"
    DATABASE_URL: str = "postgresql://postgres:codegraph_secret@localhost:5432/codegraph"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
