# tests/unit/structural/test_markdown_parser.py

# Tests for US-5.1 AC2 (YAML Frontmatter) and AC3 (Normalization/Sanitization).

from etl.connectors.markdown.parser import normalize_path, parse_markdown, strip_invalid_chars


def test_parse_markdown_with_frontmatter() -> None:
    content = "---\ntitle: Setup Guide\nauthor: admin\n---\n# Standard Markdown\nBody text."
    metadata, body = parse_markdown(content)
    assert metadata.get("title") == "Setup Guide"
    assert metadata.get("author") == "admin"
    assert body.strip() == "# Standard Markdown\nBody text."


def test_parse_markdown_without_frontmatter() -> None:
    content = "# Just Markdown\nNo frontmatter here."
    metadata, body = parse_markdown(content)
    assert metadata == {}
    assert body.strip() == "# Just Markdown\nNo frontmatter here."


def test_normalize_path() -> None:
    assert normalize_path(".\\docs\\guide.md") == "docs/guide.md"
    assert normalize_path("/docs/guide.md") == "docs/guide.md"
    assert normalize_path("./docs/guide.md") == "docs/guide.md"


def test_strip_invalid_chars() -> None:
    text = "Valid text.\x00\x08 Invalid chars."
    assert strip_invalid_chars(text) == "Valid text. Invalid chars."
