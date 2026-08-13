# etl/connectors/confluence/converter.py

# Minimalist HTML/ADF to Markdown converter ensuring core architectural
# documentation structure is preserved (US-5.3).

import re


def html_to_markdown(html: str) -> str:
    """Converts basic Confluence HTML responses to Markdown."""
    if not html:
        return ""

    text = re.sub(r"<h1>(.*?)</h1>", r"# \1\n\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<h2>(.*?)</h2>", r"## \1\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<h3>(.*?)</h3>", r"### \1\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p>(.*?)</p>", r"\1\n\n", text, flags=re.IGNORECASE)

    # Strip remaining arbitrary HTML tags (scripts, complex macros) for MVP safety
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()
