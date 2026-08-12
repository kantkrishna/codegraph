# backend/services/git_service.py

# This file handles executing shallow git clones and triggering file discovery.

import logging
import subprocess
import tempfile

from backend.models.events import FileDiscovered
from backend.services.file_traversal import traverse_repository

logger = logging.getLogger(__name__)


async def publish_file_discovered(event: FileDiscovered) -> None:
    """Placeholder for publishing to Redis PubSub/Streams for US-4.3."""
    # In full implementation, this writes to a Redis stream for the AST parser workers
    logger.debug(f"Discovered {event.language} file: {event.file_path}")


async def clone_and_process_repository(clone_url: str, repo_id: int, branch: str) -> None:
    """Clones a repo to an ephemeral directory, processes files, and cleans up."""
    # Create an ephemeral temporary directory that auto-cleans on block exit
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Cloning {clone_url} into ephemeral directory: {temp_dir}")

        # Execute shallow clone
        process = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, temp_dir], capture_output=True, text=True
        )

        if process.returncode != 0:
            logger.error(f"Git clone failed: {process.stderr}")
            raise RuntimeError(f"Clone failed for {clone_url}")

        # Traverse and publish file events
        for file_path in traverse_repository(temp_dir):
            ext = file_path.split(".")[-1]
            relative_path = file_path.replace(temp_dir + "/", "")

            event = FileDiscovered(repository_id=repo_id, file_path=relative_path, language=ext)
            await publish_file_discovered(event)

        logger.info(f"Completed ingestion traversal for {repo_id}. Ephemeral disk cleaning up.")
