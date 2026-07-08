"""Structured logging configuration for Nova AI using structlog.

Provides console logging for development and JSON logging for production environments,
with support for asynchronous context variable bindings (e.g., request tracing).
"""

import logging
from typing import Any, List, Optional
import structlog
from structlog.types import Processor


def configure_logging(log_level: str = "INFO", debug: bool = False) -> None:
    """Configures global structlog logging settings.

    Args:
        log_level: The minimum logging level to output.
        debug: True for colorized console output; False for JSON serialization.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: List[Processor] = [
        # Merges thread-local context variables (e.g. request_id, correlation_id)
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if debug:
        # Development Console Formatting
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        # Production JSON Formatting
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Returns a pre-configured bound structlog logger.

    Args:
        name: The namespace (module name) for the logger instance.

    Returns:
        An instance of a structlog bound logger.
    """
    return structlog.get_logger(name)


def bind_request_context(
    request_id: str,
    correlation_id: str,
    user_id: Optional[str] = None,
) -> None:
    """Binds request variables to the active structured log context.

    Enables request tracing across asynchronous call chains.
    """
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        correlation_id=correlation_id,
        user_id=user_id,
    )


def clear_request_context() -> None:
    """Clears context variables from the active structured log context."""
    structlog.contextvars.clear_contextvars()
