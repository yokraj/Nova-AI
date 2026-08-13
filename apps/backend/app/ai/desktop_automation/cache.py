"""In-memory cache for GUI element selectors and window maps.
"""

import time
from typing import Any, Dict, Optional


class DesktopAutomationCache:
    """In-memory cache for GUI element selectors and window trees."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if present and non-expired."""
        if key in self._store:
            entry = self._store[key]
            if time.time() - entry["timestamp"] <= self._ttl:
                return entry["data"]
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Caches item with timestamp."""
        self._store[key] = {"data": value, "timestamp": time.time()}

    def clear(self) -> None:
        """Clears cached items."""
        self._store.clear()
