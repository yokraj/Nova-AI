"""Execution Cache caching step outputs and execution results."""

import time
from typing import Any, Dict, Optional


class ExecutionCache:
    """In-memory cache for execution step outputs."""

    def __init__(self, default_ttl: int = 300) -> None:
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if unexpired."""
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry["expires_at"]:
            self._cache.pop(key, None)
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache value with expiration."""
        ttl_val = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_val,
        }

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
