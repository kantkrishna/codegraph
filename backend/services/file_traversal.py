# backend/services/file_traversal.py

# This file handles the local file system traversal of cloned repositories.

import os
from collections.abc import Iterator
from typing import Any

import pathspec

# Standard enterprise ignore patterns
GLOBAL_IGNORES = [".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"]
VALID_EXTENSIONS = {".py", ".ts", ".js", ".java", ".go", ".md"}


def get_gitignore_spec(repo_path: str) -> pathspec.PathSpec[Any]:
    """Parses the .gitignore file if it exists."""
    gitignore_path = os.path.join(repo_path, ".gitignore")
    patterns = GLOBAL_IGNORES.copy()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as f:
            patterns.extend(f.read().splitlines())
    return pathspec.PathSpec.from_lines("gitignore", patterns)


def traverse_repository(repo_path: str) -> Iterator[str]:
    """Walks the directory yielding valid source files respecting ignores."""
    spec = get_gitignore_spec(repo_path)

    for root, dirs, files in os.walk(repo_path):
        # Relativize path for pathspec evaluation
        rel_root = os.path.relpath(root, repo_path)
        if rel_root == ".":
            rel_root = ""

        # Modify dirs in-place to prune ignored directories (stops os.walk from descending)
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(rel_root, d))]

        for file in files:
            rel_file_path = os.path.join(rel_root, file)
            _, ext = os.path.splitext(file)

            if ext in VALID_EXTENSIONS and not spec.match_file(rel_file_path):
                yield os.path.join(repo_path, rel_file_path)
