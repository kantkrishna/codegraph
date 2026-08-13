# backend/domain/events/ingestion.py
#
# This file defines the specific polymorphic payloads for ingestion events
# like RepositoryIndexed, CommitDetected, ServiceAdded, and DocumentationUpdated.

from typing import Any, Literal

from pydantic import BaseModel, TypeAdapter

from backend.domain.events.base import CodeGraphEvent


# --- Payloads ---
class RepositoryIndexedPayload(BaseModel):
    repository_url: str
    commit_hash: str


class CommitDetectedPayload(BaseModel):
    repository_url: str
    branch: str
    commit_hash: str
    author: str


class ServiceAddedPayload(BaseModel):
    service_name: str
    language: str
    repository_url: str


class DocumentationUpdatedPayload(BaseModel):
    document_url: str
    document_type: str
    repository_url: str
    # Evolved for Epic 5 to hold the extracted Markdown and headers
    content: str | None = None
    title: str | None = None


class DocumentationLinkedPayload(BaseModel):
    doc_id: str
    node_id: str
    entity_name: str
    confidence: float


# backend/domain/events/ingestion.py
#
# This file defines the specific ingestion events used in Epic 4 and Epic 5.
# (Note: Keep your existing Epic 3 models like RepositoryIndexedEvent untouched above these)


class FileDiscovered(CodeGraphEvent[Any]):
    type: str = "FileDiscovered"
    repository: str
    file_path: str
    content: str
    data: Any | None = None  # Override required base field for this specific event


class DocumentationUpdated(CodeGraphEvent[Any]):
    type: str = "DocumentationUpdated"
    repository: str
    file_path: str
    metadata: dict[str, Any]
    content: str
    data: Any | None = None  # Override required base field for this specific event


class ADRCreated(CodeGraphEvent[Any]):
    type: str = "ADRCreated"
    repository: str
    file_path: str
    metadata: dict[str, Any]
    content: str
    status: str | None = None
    decision: str | None = None
    data: Any | None = None  # Override required base field for this specific event


# --- Events ---
class RepositoryIndexedEvent(CodeGraphEvent[RepositoryIndexedPayload]):
    type: Literal["RepositoryIndexed"] = "RepositoryIndexed"


class CommitDetectedEvent(CodeGraphEvent[CommitDetectedPayload]):
    type: Literal["CommitDetected"] = "CommitDetected"


class ServiceAddedEvent(CodeGraphEvent[ServiceAddedPayload]):
    type: Literal["ServiceAdded"] = "ServiceAdded"


class DocumentationUpdatedEvent(CodeGraphEvent[DocumentationUpdatedPayload]):
    type: Literal["DocumentationUpdated"] = "DocumentationUpdated"


class DocumentationLinkedEvent(CodeGraphEvent[DocumentationLinkedPayload]):
    type: Literal["DocumentationLinked"] = "DocumentationLinked"


# --- Polymorphic Router ---
IngestionEvent = (
    RepositoryIndexedEvent | CommitDetectedEvent | ServiceAddedEvent | DocumentationUpdatedEvent
)

# TypeAdapter configured with a discriminator allows mapping arbitrary dictionaries
# to the correct specific Event class based on the 'type' field.
_event_adapter: TypeAdapter[IngestionEvent] = TypeAdapter(IngestionEvent)


def parse_ingestion_event(payload: dict[str, Any]) -> IngestionEvent:
    """
    Parses a raw dictionary into the appropriate specific CodeGraphEvent subtype.
    Raises pydantic.ValidationError if invalid.
    """
    return _event_adapter.validate_python(payload)
