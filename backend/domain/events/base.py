# backend/domain/events/base.py
#
# This file defines the core CloudEvents base model for all CodeGraph events.

from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class CodeGraphEvent[T](BaseModel):
    """
    Base event model implementing the CloudEvents v1.0 specification.
    """

    id: UUID = Field(default_factory=uuid4)
    source: str
    specversion: str = "1.0"
    type: str
    datacontenttype: str = "application/json"
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: T
