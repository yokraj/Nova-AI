"""Memory Store Module.

Provides low-level cached memory buffer management and multi-tiered in-memory index fallback.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.schemas import MemoryEntryResponse, MemoryEntryCreate
from app.memory.exceptions import MemoryNotFoundError

logger = structlog.get_logger(__name__)


class MemoryStore:
    """Enterprise In-Memory Fast Cache & Tier Buffer Manager."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info("memory_store_initialized")

    def put(self, memory_id: str, data: Dict[str, Any]) -> None:
        """Puts memory entry into fast cache buffer."""
        self._cache[memory_id] = data
        logger.debug("memory_cached", memory_id=memory_id)

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves memory entry from fast cache buffer."""
        return self._cache.get(memory_id)

    def remove(self, memory_id: str) -> bool:
        """Evicts memory entry from cache."""
        if memory_id in self._cache:
            del self._cache[memory_id]
            return True
        return False

    def clear(self) -> None:
        """Clears all cached entries."""
        self._cache.clear()

    def size(self) -> int:
        """Returns active cached item count."""
        return len(self._cache)
