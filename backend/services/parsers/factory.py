# backend/services/parsers/factory.py

# Routes discovered files to the correct AST or Manifest parser and publishes events.

import logging
import os
import uuid
from typing import Any

from backend.core.events.broker import event_broker
from backend.core.events.publisher import EventPublisher
from backend.domain.events.ingestion import ADRCreated, DocumentationUpdated
from backend.models.events import FileDiscovered
from backend.services.parsers.manifest_parser import ManifestParser
from backend.services.parsers.python_parser import PythonParser
from etl.connectors.markdown.adr_parser import extract_decision, extract_status, is_adr
from etl.connectors.markdown.parser import normalize_path, parse_markdown, strip_invalid_chars

logger = logging.getLogger(__name__)

# Initialize parsers globally to avoid reloading grammars
_PY_PARSER = PythonParser()
_MANIFEST_PARSER = ManifestParser()

# Initialize the Event Bus connection
_EVENT_BUS = EventPublisher(event_broker)


async def publish_event(event: Any) -> None:
    """Serializes the Pydantic event and pushes it to the Kafka broker."""
    topic = "events.knowledge.extracted"
    await _EVENT_BUS.publish(topic, event)


async def process_discovered_file(event: FileDiscovered, clone_dir: str) -> None:
    """Reads the file from disk, parses its AST, Manifest, or ADR/Markdown, and emits events."""
    full_path = os.path.join(clone_dir, event.file_path)
    if not os.path.exists(full_path):
        return
    try:
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

        # 3. Process Markdown & ADRs (US-5.1 & US-5.2)
        elif event.language in ("md", "markdown") or event.file_path.endswith(".md"):
            text_content = source_code.decode("utf-8", errors="ignore")
            clean_path = normalize_path(event.file_path)
            clean_content = strip_invalid_chars(text_content)
            metadata, body = parse_markdown(clean_content)
            event_id = str(uuid.uuid4())
            repo_str = str(event.repository_id)

            if is_adr(clean_path):
                status = extract_status(body)
                decision = extract_decision(body)
                adr_event = ADRCreated(
                    id=event_id,
                    source="markdown_parser",
                    repository=repo_str,
                    file_path=clean_path,
                    metadata=metadata,
                    content=body,
                    status=status,
                    decision=decision,
                )
                await publish_event(adr_event)
            else:
                doc_event = DocumentationUpdated(
                    id=event_id,
                    source="markdown_parser",
                    repository=repo_str,
                    file_path=clean_path,
                    metadata=metadata,
                    content=body,
                )
                await publish_event(doc_event)

    except Exception as e:
        logger.error(f"Failed to process file {event.file_path}: {str(e)}", exc_info=True)