"""Automation Context storing active page references, window handles, and extracted data across steps."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("automation_context")


class AutomationContext:
    """Thread-safe context store for desktop and browser automation."""

    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store key value pair."""
        self._store[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve stored value."""
        return self._store.get(key, default)

    def clear(self) -> None:
        """Clear context."""
        self._store.clear()
