# etl/connectors/markdown/parser.py

# Utilities for parsing standard Markdown files, extracting YAML frontmatter,
# and normalizing text as required by US-5.1.

import re
from typing import Any

import yaml

FRONTMATTER_PATTERN = re.compile(r"^-{3,}\s*\n(.*?)\n-{3,}\s*\n(.*)", re.DOTALL)


def parse_markdown(content: str) -> tuple[dict[str, Any], str]:
    """Extracts YAML frontmatter from markdown content."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_text, body = match.groups()
    try:
        metadata = yaml.safe_load(yaml_text)
        if not isinstance(metadata, dict):
            metadata = {}
    except yaml.YAMLError:
        metadata = {}

    return metadata, body


def normalize_path(path: str) -> str:
    """Normalizes Windows paths and removes leading relative indicators."""
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    elif normalized.startswith("/"):
        normalized = normalized[1:]
    return normalized


def strip_invalid_chars(text: str) -> str:
    """Removes null bytes and control characters (except standard whitespace)."""
    return re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)
