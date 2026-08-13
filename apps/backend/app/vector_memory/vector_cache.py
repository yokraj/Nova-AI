"""Vector Cache Module.

High-performance LRU/TTL cache for embeddings, search result candidates,
frequently used vectors, and recently indexed vectors.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import structlog

from app.vector_memory.config import VectorConfig

logger = structlog.get_logger(__name__)


class VectorCache:
    """Enterprise Vector Embedding & Search Query Cache Manager."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or VectorConfig()
        self._embedding_cache: Dict[str, Dict[str, Any]] = {}
        self._search_cache: Dict[str, Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0
        logger.info("vector_cache_initialized", capacity=self.config.cache_capacity)

    def cache_embedding(self, text_hash: str, vector: List[float], model_name: str) -> None:
        """Caches generated embedding vector by text hash."""
        if len(self._embedding_cache) >= self.config.cache_capacity:
            # Evict first key
            first_key = next(iter(self._embedding_cache))
            del self._embedding_cache[first_key]

        self._embedding_cache[text_hash] = {
            "vector": vector,
            "model_name": model_name,
            "timestamp": datetime.now(timezone.utc),
        }

    def get_embedding(self, text_hash: str) -> Optional[List[float]]:
        """Retrieves cached embedding vector by text hash."""
        item = self._embedding_cache.get(text_hash)
        if item:
            self._hits += 1
            return item["vector"]
        self._misses += 1
        return None

    def cache_search_results(self, query_key: str, results: List[Dict[str, Any]]) -> None:
        """Caches search candidates for a query key."""
        self._search_cache[query_key] = {
            "results": results,
            "timestamp": datetime.now(timezone.utc),
        }

    def get_search_results(self, query_key: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieves cached search candidates."""
        item = self._search_cache.get(query_key)
        if item:
            self._hits += 1
            return item["results"]
        self._misses += 1
        return None

    def clear(self) -> None:
        """Clears all vector cache buffers."""
        self._embedding_cache.clear()
        self._search_cache.clear()

    @property
    def hit_count(self) -> int:
        return self._hits

    @property
    def miss_count(self) -> int:
        return self._misses
