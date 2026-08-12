# tests/unit/structural/test_git_service.py

# This file contains unit tests for the ephemeral git cloning service and file traversal.

from pathlib import Path
from typing import Any

import pytest

from backend.services.file_traversal import traverse_repository
from backend.services.git_service import clone_and_process_repository


@pytest.mark.asyncio
async def test_clone_and_process_repository_success(mocker: Any) -> None:
    """Test that the clone service creates a temp dir, calls git, traverses, and cleans up."""
    mock_run = mocker.patch("backend.services.git_service.subprocess.run")
    mock_run.return_value.returncode = 0

    # Return a fake file so the publishing loop executes exactly once
    mock_traverse = mocker.patch(
        "backend.services.git_service.traverse_repository", return_value=["src/main.py"]
    )
    mock_publish = mocker.patch("backend.services.git_service.publish_file_discovered")

    await clone_and_process_repository("https://github.com/test/repo.git", 123, "main")

    mock_run.assert_called_once()
    assert "clone" in mock_run.call_args[0][0]
    assert "--depth" in mock_run.call_args[0][0]
    mock_traverse.assert_called_once()
    mock_publish.assert_called_once()


def test_traverse_repository_filters_correctly(tmp_path: Path) -> None:
    """Test that file traversal ignores .git, node_modules, and binary files."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    # Create valid files
    (repo_dir / "main.py").touch()
    (repo_dir / "app.ts").touch()

    # Create ignored directories
    git_dir = repo_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").touch()

    node_modules = repo_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "lib.js").touch()

    # Create a gitignore file
    gitignore = repo_dir / ".gitignore"
    gitignore.write_text("ignored.py\n")
    (repo_dir / "ignored.py").touch()

    files = list(traverse_repository(str(repo_dir)))

    file_names = [Path(f).name for f in files]
    assert "main.py" in file_names
    assert "app.ts" in file_names
    assert "config" not in file_names
    assert "lib.js" not in file_names
    assert "ignored.py" not in file_names
