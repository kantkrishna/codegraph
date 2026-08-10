# tests/unit/foundation/test_logger.py

# This file contains unit tests for the structlog configuration and redaction logic.

import json
from io import StringIO

import pytest
import structlog

from backend.core.logger import redact_sensitive_data, setup_logging


@pytest.fixture
def log_output() -> StringIO:
    """Captures structlog output for assertions."""
    stream = StringIO()
    setup_logging(stream=stream)
    return stream


def test_logger_outputs_json(log_output: StringIO) -> None:
    """AC 1: Verify that the logger outputs strict JSON."""
    logger = structlog.get_logger("test_logger")
    logger.info("system_boot", environment="test")

    output = log_output.getvalue()
    log_dict = json.loads(output)

    assert log_dict["event"] == "system_boot"
    assert log_dict["environment"] == "test"
    assert "timestamp" in log_dict
    assert "level" in log_dict


def test_sensitive_data_redaction() -> None:
    """AC 4: Verify that sensitive keys are masked before logging."""
    event_dict = {
        "event": "user_login",
        "authorization": "Bearer secret_token_123",
        "api_key": "sk-123456",
        "safe_key": "safe_value",
    }

    redacted_dict = redact_sensitive_data(None, "info", event_dict)

    assert redacted_dict["authorization"] == "***REDACTED***"
    assert redacted_dict["api_key"] == "***REDACTED***"
    assert redacted_dict["safe_key"] == "safe_value"
