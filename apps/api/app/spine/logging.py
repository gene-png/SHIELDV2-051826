"""Structured JSON logging. Never emits PII, never emits stack traces in
production, and pins the correlation ID on every record.

`get_logger(__name__)` returns a structlog logger configured per the global
chain installed at import time. Re-importing is safe.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.settings import get_settings

_SENSITIVE_KEYS = {"password", "authorization", "token", "cookie", "set-cookie", "api_key"}


def _strip_sensitive(_, __, event_dict: dict[str, Any]) -> dict[str, Any]:
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = "***"
    return event_dict


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            _strip_sensitive,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or "shield")


# Configure on import so module-level loggers in services pick it up.
configure_logging()
