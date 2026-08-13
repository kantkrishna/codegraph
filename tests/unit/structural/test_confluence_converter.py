# tests/unit/structural/test_confluence_converter.py

# Tests for US-5.3 AC3 (HTML/ADF to Markdown Conversion).

from etl.connectors.confluence.converter import html_to_markdown


def test_html_to_markdown_headers_and_paragraphs() -> None:
    html = "<h1>Auth Service</h1><p>This handles logins.</p><h2>API</h2><p>Rest API</p>"
    md = html_to_markdown(html)
    assert "# Auth Service" in md
    assert "This handles logins." in md
    assert "## API" in md
