import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.security import redact_secrets


class JsonLogFormatter(logging.Formatter):
    def __init__(self, service: str) -> None:
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.service,
            "component": record.name,
            "event": record.getMessage(),
        }
        for key in (
            "request_id",
            "scan_id",
            "signal_id",
            "pair",
            "error_code",
            "duration_ms",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info and record.exc_info[0] is not None:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(redact_secrets(payload), ensure_ascii=False, default=str)


def configure_logging(service: str, level: str) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter(service))
    root.addHandler(handler)
    root.setLevel(level.upper())
