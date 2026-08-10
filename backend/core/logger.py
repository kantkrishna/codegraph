# backend/core/logger.py

# This file configures the enterprise structlog setup and data redaction processors.

import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog

SENSITIVE_KEYS = {"authorization", "api_key", "password", "secret", "token"}


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Structlog processor to mask sensitive data based on key names."""
    for key, value in event_dict.items():
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
        elif isinstance(value, dict):
            # Recursively redact nested dictionaries (e.g., headers)
            event_dict[key] = redact_sensitive_data(logger, method_name, value.copy())
    return event_dict


def setup_logging(stream: Any = sys.stdout) -> None:
    """Initializes JSON structured logging globally, integrating with standard logging."""

    # 1. Intercept standard Python logging and route it to our stream (stdout or pytest capsys)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    # Clear any existing handlers to prevent duplicate logs
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    # 2. Configure structlog to use standard library logging as its backend
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # Pulls request_id from context
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,  # Safely extracts logger name now
            structlog.processors.TimeStamper(fmt="iso"),
            redact_sensitive_data,
            structlog.processors.JSONRenderer(),  # AC 1: Strictly JSON output
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),  # Connects structlog to stdlib
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
