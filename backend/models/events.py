# backend/models/events.py
#
# This file defines the strictly typed Pydantic models for the Event-Driven Architecture.


from pydantic import BaseModel, Field


class RepositoryIngestionRequested(BaseModel):
    repository_url: str
    repository_id: int
    branch: str


class FileDiscovered(BaseModel):
    repository_id: int
    file_path: str
    language: str


class EntityExtracted(BaseModel):
    repository_id: int
    file_path: str
    entity_type: str = Field(..., description="Class, Function, Interface, etc.")
    name: str
    docstring: str | None = None


class RelationshipExtracted(BaseModel):
    repository_id: int
    source_file: str
    target_module: str
    relationship_type: str = Field(..., description="IMPORTS, INHERITS, CALLS")


class DependencyDetected(BaseModel):
    repository_id: int
    file_path: str
    package_name: str
    version_constraint: str | None = None
