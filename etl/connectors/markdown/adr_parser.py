# etl/connectors/markdown/adr_parser.py

# Heuristics and regex extraction for Architecture Decision Records (ADRs)
# as required by US-5.2.

import re

# Matches /docs/adr/, /architecture/decisions/, etc.
ADR_PATH_PATTERN = re.compile(r"(^|/)(adr|decisions)(/|$)", re.IGNORECASE)

# Matches '## Status', '### status:', etc. and captures the next line
STATUS_PATTERN = re.compile(r"#+\s*Status:?\s*\n+([^\n]+)", re.IGNORECASE)

# Matches '## Decision', and captures everything until the next header or EOF
DECISION_PATTERN = re.compile(r"#+\s*Decision:?\s*\n+([\s\S]*?)(?=\n#+|$)", re.IGNORECASE)


def is_adr(path: str) -> bool:
    """Uses path heuristics to determine if a markdown file is an ADR."""
    return bool(ADR_PATH_PATTERN.search(path))


def extract_status(content: str) -> str | None:
    """Extracts the status block from a MADR document."""
    match = STATUS_PATTERN.search(content)
    return match.group(1).strip() if match else None


def extract_decision(content: str) -> str | None:
    """Extracts the main decision block from a MADR document."""
    match = DECISION_PATTERN.search(content)
    return match.group(1).strip() if match else None
