# backend/domain/events/base.py
#
# This file defines the base CloudEvents compliant schema for all CodeGraph events.

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class CodeGraphEvent[T](BaseModel):
    """Base event model following a simplified CloudEvents specification."""

    # Union allows Epic 3 to receive a UUID object, while Epic 5 can pass string IDs
    id: uuid.UUID | str = Field(default_factory=uuid.uuid4, description="Unique event identifier")
    source: str = Field(..., description="System emitting the event")
    type: str = Field(..., description="The type of the event")
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # CloudEvents 1.0 specification fields required by Epic 3 tests
    specversion: str = Field(default="1.0", description="CloudEvents specification version")
    datacontenttype: str = Field(
        default="application/json", description="Content type of the data payload"
    )

    # Strictly required to satisfy Epic 3 validation tests
    data: T
