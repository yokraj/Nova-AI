"""Assistant Cache for storing plans and context objects."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("assistant_cache")


class AssistantCache:
    """In-memory cache for assistant plans, context, and recommendations."""

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached item."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Store item in cache."""
        self._cache[key] = value

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
