# backend/models/events.py

# This file defines the strictly typed Pydantic models for the Event-Driven Architecture.


from typing import Any

from pydantic import Field

from backend.domain.events.base import CodeGraphEvent


class RepositoryIngestionRequested(CodeGraphEvent[Any]):
    type: str = "RepositoryIngestionRequested"
    source: str = "github_webhook"
    repository_url: str
    repository_id: int
    branch: str
    data: Any | None = None


class FileDiscovered(CodeGraphEvent[Any]):
    type: str = "FileDiscovered"
    source: str = "git_service"
    repository_id: int
    file_path: str
    language: str
    data: Any | None = None


class EntityExtracted(CodeGraphEvent[Any]):
    type: str = "EntityExtracted"
    source: str = "ast_parser"
    repository_id: int
    file_path: str
    entity_type: str = Field(..., description="Class, Function, Interface, etc.")
    name: str
    docstring: str | None = None
    data: Any = None


class RelationshipExtracted(CodeGraphEvent[Any]):
    type: str = "RelationshipExtracted"
    source: str = "ast_parser"
    repository_id: int
    source_file: str
    target_module: str
    relationship_type: str = Field(..., description="IMPORTS, INHERITS, CALLS")
    data: Any = None


class DependencyDetected(CodeGraphEvent[Any]):
    type: str = "DependencyDetected"
    source: str = "manifest_parser"
    repository_id: int
    file_path: str
    package_manager: str
    package_name: str
    version_constraint: str | None = None
    data: Any = None
