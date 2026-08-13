"""In-memory cache for kernel execution plans and intent lookups.
"""

import time
from typing import Any, Dict, Optional


class KernelCache:
    """In-memory cache storing intent parses, capability matches, and plans."""

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
