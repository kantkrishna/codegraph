# backend/services/parsers/factory.py

# Routes discovered files to the correct AST or Manifest parser and publishes events.

import logging
import os
from typing import Any

from backend.core.events.broker import event_broker
from backend.core.events.publisher import EventPublisher
from backend.models.events import (
    FileDiscovered,
)
from backend.services.parsers.manifest_parser import ManifestParser
from backend.services.parsers.python_parser import PythonParser

logger = logging.getLogger(__name__)

# Initialize parsers globally to avoid reloading grammars
_PY_PARSER = PythonParser()
_MANIFEST_PARSER = ManifestParser()

# Initialize the Event Bus connection using Dependency Injection with Kafka/Redis broker URL
_EVENT_BUS = EventPublisher(event_broker)


async def publish_event(event: Any) -> None:
    """
    Serializes the Pydantic event and pushes it to the Epic 3 Event Bus.
    """
    # Determine the correct topic based on the event type
    topic = "events.knowledge.extracted"

    # Pass the raw Pydantic event object, NOT serialized bytes.
    # EventPublisher.publish() handles the model_dump_json() serialization securely.
    await _EVENT_BUS.publish(topic, event)


async def process_discovered_file(event: FileDiscovered, clone_dir: str) -> None:
    """
    Reads the file from disk, parses its AST or Manifest, and emits structural events.
    """
    full_path = os.path.join(clone_dir, event.file_path)

    if not os.path.exists(full_path):
        return

    try:
        # Move the open() inside the try block to safely handle read errors
        with open(full_path, "rb") as f:
            source_code = f.read()

        # 1. Process Package Manifests (US-4.4)
        if event.file_path.endswith(("requirements.txt", "package.json")):
            deps = _MANIFEST_PARSER.parse_manifest(
                source_code, event.repository_id, event.file_path
            )
            for dep in deps:
                await publish_event(dep)

        # 2. Process Python ASTs (US-4.3 & US-4.4)
        elif event.language in ("py", "python"):
            entities, relationships = _PY_PARSER.parse(
                source_code, event.repository_id, event.file_path
            )
            for ent in entities:
                await publish_event(ent)
            for rel in relationships:
                await publish_event(rel)

    except Exception as e:
        # Log the error and continue processing other files
        logger.error(f"Failed to process file {event.file_path}: {str(e)}", exc_info=True)
