# backend/models/events.py

# This file defines the strictly typed Pydantic models for the Event-Driven Architecture.

from pydantic import BaseModel, Field


class RepositoryIngestionRequested(BaseModel):
    repository_url: str = Field(..., description="The HTTPS clone URL of the repository")
    repository_id: int = Field(..., description="GitHub's internal repository ID")
    branch: str = Field(..., description="The branch or ref to clone")


class FileDiscovered(BaseModel):
    repository_id: int = Field(..., description="GitHub's internal repository ID")
    file_path: str = Field(..., description="Relative path of the file within the repository")
    language: str = Field(..., description="Inferred programming language based on extension")
