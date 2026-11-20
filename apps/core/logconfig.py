from typing import Any

import structlog

# Applied to every log line, from our code (structlog) or Django's (stdlib logging).
SHARED_PROCESSORS: list[Any] = [
    structlog.contextvars.merge_contextvars,  # adds request_id
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
]


def build_logging_config(level: str) -> dict[str, Any]:
    """Send all logs through one JSON formatter. Returns Django's LOGGING dict."""
    structlog.configure(
        processors=[*SHARED_PROCESSORS, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": SHARED_PROCESSORS,
            },
        },
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
        "root": {"handlers": ["console"], "level": level},
    }
