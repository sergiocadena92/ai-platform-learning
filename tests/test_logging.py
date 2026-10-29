import json
import logging
import sys

from app.logging_config import JsonFormatter


def test_json_formatter_creates_valid_json():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)
    log_data = json.loads(result)

    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "app.test"
    assert log_data["message"] == "Test message"


def test_json_formatter_includes_extra_fields():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Request completed",
        args=(),
        exc_info=None,
    )

    record.request_id = "test-123"
    record.status_code = 200
    record.duration_ms = 42.5

    log_data = json.loads(formatter.format(record))

    assert log_data["request_id"] == "test-123"
    assert log_data["status_code"] == 200
    assert log_data["duration_ms"] == 42.5
    assert isinstance(
        log_data["status_code"],
        int,
    )
    assert isinstance(
        log_data["duration_ms"],
        float,
    )


def test_json_formatter_uses_default_request_id():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Outside request",
        args=(),
        exc_info=None,
    )

    log_data = json.loads(formatter.format(record))

    assert log_data["request_id"] == "-"


def test_json_formatter_includes_exception_info():
    formatter = JsonFormatter()

    try:
        raise ValueError("Invalid market response")
    except ValueError:
        record = logging.LogRecord(
            name="app.test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Market request failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    log_data = json.loads(formatter.format(record))

    assert "exception" in log_data
    assert "ValueError: Invalid market response" in log_data["exception"]
