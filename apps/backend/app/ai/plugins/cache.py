"""Plugin Cache caching capability lookups and execution results."""

from typing import Any, Dict, Optional
import time


class PluginCache:
    """In-memory cache for execution results and capability lookups."""

    def __init__(self, default_ttl: int = 300) -> None:
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve unexpired value."""
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry["expires_at"]:
            self._cache.pop(key, None)
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value with expiration."""
        ttl_val = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_val,
        }

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
