"""Shared Context tracking mission metadata and task dependencies."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("shared_context")


class SharedContext:
    """Shared task context and mission metadata board."""

    def __init__(self) -> None:
        self._context: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set shared context key."""
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get shared context value."""
        return self._context.get(key, default)
