"""In-memory cache for mission records, progress reports, and workflow definitions.
"""

import time
from typing import Any, Dict, Optional


class MissionCache:
    """In-memory cache for long-running mission data and workflow definitions."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if present and not expired."""
        if key in self._store:
            entry = self._store[key]
            if time.time() - entry["timestamp"] <= self._ttl:
                return entry["data"]
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Caches item with current timestamp."""
        self._store[key] = {"data": value, "timestamp": time.time()}

    def clear(self) -> None:
        """Clears all cached entries."""
        self._store.clear()
