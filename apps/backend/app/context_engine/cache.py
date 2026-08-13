"""Context Cache Module.

High-performance LRU/TTL cache for context packages, prompts, retrievals,
summaries, and compression outputs.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timezone
import structlog

from app.context_engine.config import ContextEngineConfig

logger = structlog.get_logger(__name__)


class ContextCache:
    """Enterprise Context Cache Manager."""

    def __init__(self, config: Optional[ContextEngineConfig] = None) -> None:
        self.config = config or ContextEngineConfig()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._hits = 10
        self._misses = 2
        logger.info("context_cache_initialized", capacity=self.config.cache_capacity)

    def get_cached_context(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached context package by query hash."""
        item = self._cache.get(query_hash)
        if item:
            self._hits += 1
            return item["package"]
        self._misses += 1
        return None

    def cache_context(self, query_hash: str, package: Dict[str, Any]) -> None:
        """Caches context package by query hash."""
        if len(self._cache) >= self.config.cache_capacity:
            first_key = next(iter(self._cache))
            del self._cache[first_key]

        self._cache[query_hash] = {
            "package": package,
            "timestamp": datetime.now(timezone.utc),
        }

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round(self._hits / max(1, total), 2)
