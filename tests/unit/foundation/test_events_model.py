# tests/unit/foundation/test_events_model.py
#
# This file contains unit tests for the Engineering Event Data Model (US-3.2).
# It tests strict CloudEvent schema compliance, polymorphic routing, and validation failures.

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from backend.domain.events.ingestion import (
    CommitDetectedEvent,
    CommitDetectedPayload,
    RepositoryIndexedEvent,
    RepositoryIndexedPayload,
    ServiceAddedEvent,
    parse_ingestion_event,
)


def test_cloud_events_base_specification() -> None:
    """Validate that the base CodeGraphEvent complies with CloudEvents 1.0."""
    # We must pass a RepositoryIndexedPayload instance, not a dictionary
    event = RepositoryIndexedEvent(
        source="urn:codegraph:github_connector",
        data=RepositoryIndexedPayload(
            repository_url="https://github.com/org/repo", commit_hash="a1b2c3d4"
        ),
    )

    # Assert standard CloudEvents fields exist and default properly
    assert isinstance(event.id, UUID)
    assert event.specversion == "1.0"
    assert event.datacontenttype == "application/json"
    assert event.type == "RepositoryIndexed"
    assert event.source == "urn:codegraph:github_connector"
    assert isinstance(event.time, datetime)
    assert event.time.tzinfo == UTC


def test_commit_detected_event_schema() -> None:
    """Validate the CommitDetected specific payload."""
    # We must pass a CommitDetectedPayload instance, not a dictionary
    event = CommitDetectedEvent(
        source="github_webhook",
        data=CommitDetectedPayload(
            repository_url="https://github.com/org/repo",
            branch="main",
            commit_hash="f9e8d7c6",
            author="jane.doe@example.com",
        ),
    )
    assert event.data.branch == "main"
    assert event.data.author == "jane.doe@example.com"


def test_polymorphic_event_parsing() -> None:
    """Validate that Pydantic Discriminator correctly routes raw JSON to the right class."""
    raw_event: dict[str, Any] = {
        "source": "urn:codegraph:system",
        "type": "ServiceAdded",
        "data": {
            "service_name": "payment-service",
            "language": "python",
            "repository_url": "https://github.com/org/payments",
        },
    }

    parsed_event = parse_ingestion_event(raw_event)
    assert isinstance(parsed_event, ServiceAddedEvent)
    assert parsed_event.data.service_name == "payment-service"


def test_invalid_payload_fails_validation() -> None:
    """Validate that missing required fields or unknown types fail immediately."""

    # Missing required 'data' field
    with pytest.raises(ValidationError):
        RepositoryIndexedEvent(source="urn:test")  # type: ignore

    # Unknown event type in polymorphic parser
    invalid_raw_event: dict[str, Any] = {
        "source": "urn:test",
        "type": "UnknownEvent",
        "data": {"some": "data"},
    }

    with pytest.raises(ValidationError):
        parse_ingestion_event(invalid_raw_event)
