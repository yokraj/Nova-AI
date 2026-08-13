"""Cache layer storing completed execution results.
"""

from typing import Any, Optional

class AgentCache:
    """FIFO cache structure mapping execution IDs to results."""

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached outcome by ID."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Stores outcome mapping, removing oldest entry if full."""
        if len(self._cache) >= self.max_size:
            first_key = next(iter(self._cache))
            self._cache.pop(first_key)
        self._cache[key] = value
