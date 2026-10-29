import logging
from app.request_context import request_id_var
from logging.config import dictConfig
import json
import logging

from datetime import datetime, timezone
from logging.config import dictConfig

from app.request_context import request_id_var


class RequestContextFilter(logging.Filter):
    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(log_level: str) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_context": {
                    "()": RequestContextFilter,
                },
            },
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "filters": ["request_context"],
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "httpx": {
                    "level": "WARNING",
                },
                "httpcore": {
                    "level": "WARNING",
                },
            },
        }
    )


STANDARD_LOG_RECORD_ATTRIBUTES = set(logging.makeLogRecord({}).__dict__.keys()) | {
    "message",
    "asctime",
}


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(
                record,
                "request_id",
                "-",
            ),
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in STANDARD_LOG_RECORD_ATTRIBUTES and key not in log_data:
                log_data[key] = value

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            log_data,
            ensure_ascii=False,
            default=str,
        )
