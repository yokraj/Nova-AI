"""Base service layer template for Nova AI services.

Exposes logging adapters and common validation helpers used across application services.
"""

from typing import Any
import structlog


class BaseService:
    """Base service class providing shared domain operation utilities."""

    def __init__(self) -> None:
        """Initializes the service and binds class-specific structured logger."""
        self.logger = structlog.get_logger(self.__class__.__name__)

    def log_info(self, event: str, **kwargs: Any) -> None:
        """Logs structured information events.

        Args:
            event: The logging event message string.
            kwargs: Dictionary of values to append to the log event.
        """
        self.logger.info(event, **kwargs)

    def log_error(self, event: str, **kwargs: Any) -> None:
        """Logs structured error events.

        Args:
            event: The logging error message string.
            kwargs: Dictionary of values to append to the log event.
        """
        self.logger.error(event, **kwargs)
