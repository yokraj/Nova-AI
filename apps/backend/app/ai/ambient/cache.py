"""Ambient Cache storing desktop snapshots and suggestions."""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("ambient_cache")


class AmbientCache:
    """In-memory cache for ambient desktop context snapshots and active suggestions."""

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
