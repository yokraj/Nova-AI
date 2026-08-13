"""OS Runtime Cache managing in-memory state caching.
"""

import time
from typing import Any, Dict, Optional


class OSRuntimeCache:
    """In-memory state cache for OS runtime metadata and state snapshots."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if not expired."""
        if key in self._store:
            entry = self._store[key]
            if time.time() - entry["timestamp"] <= self.ttl_seconds:
                return entry["value"]
        return None

    def set(self, key: str, value: Any) -> None:
        """Stores item in cache."""
        self._store[key] = {"value": value, "timestamp": time.time()}
