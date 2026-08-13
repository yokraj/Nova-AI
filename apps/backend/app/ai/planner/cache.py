"""Cache layer storing compiled execution plans.
"""

from typing import Any, Optional

class PlannerCache:
    """FIFO cache structure mapping goal descriptions to PlanningResponses."""

    def __init__(self, max_size: int = 50) -> None:
        self.max_size = max_size
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached response by goal key."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Stores response mapping, purging oldest entry if full."""
        if len(self._cache) >= self.max_size:
            first_key = next(iter(self._cache))
            self._cache.pop(first_key)
        self._cache[key] = value
