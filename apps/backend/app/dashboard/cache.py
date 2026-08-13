"""Dashboard Cache Service Module.

Provides an in-memory cache abstraction with configurable TTL support, key deletion,
and targeted invalidation capabilities for dashboard overview, metrics, and notifications.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class CacheEntry:
    """Represents an in-memory cache entry with expiration timestamp."""

    def __init__(self, value: Any, ttl_seconds: int = 60) -> None:
        self.value = value
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    @property
    def is_expired(self) -> bool:
        """Returns True if the cache entry has passed its expiration timestamp."""
        return datetime.now(timezone.utc) >= self.expires_at


class DashboardCacheService:
    """In-memory Dashboard Cache Service with TTL support.
    
    Provides key-value caching mechanics, automatic TTL expiration checks,
    and targeted namespace invalidation helpers.
    """

    def __init__(self, default_ttl: int = 60) -> None:
        self.default_ttl = default_ttl
        self._store: Dict[str, CacheEntry] = {}
        logger.info("dashboard_cache_service_initialized", default_ttl=default_ttl)

    async def get(self, key: str) -> Optional[Any]:
        """Retrieves cached value for key if present and not expired."""
        entry = self._store.get(key)
        if entry is None:
            return None

        if entry.is_expired:
            logger.debug("cache_entry_expired", key=key)
            del self._store[key]
            return None

        return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stores key-value pair in cache with specified TTL in seconds."""
        effective_ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = CacheEntry(value, ttl_seconds=effective_ttl)
        logger.debug("cache_entry_set", key=key, ttl=effective_ttl)
        return True

    async def delete(self, key: str) -> bool:
        """Deletes specific key from cache."""
        if key in self._store:
            del self._store[key]
            logger.info("cache_entry_deleted", key=key)
            return True
        return False

    async def clear(self) -> bool:
        """Flushes all entries from in-memory cache."""
        count = len(self._store)
        self._store.clear()
        logger.info("cache_cleared", entries_removed=count)
        return True

    async def invalidate_dashboard(self) -> int:
        """Invalidates all cache keys prefixed with 'dashboard:'."""
        keys_to_del = [k for k in self._store if k.startswith("dashboard:")]
        for k in keys_to_del:
            del self._store[k]
        logger.info("cache_invalidated_dashboard", count=len(keys_to_del))
        return len(keys_to_del)

    async def invalidate_metrics(self) -> int:
        """Invalidates all cache keys prefixed with 'metrics:'."""
        keys_to_del = [k for k in self._store if k.startswith("metrics:")]
        for k in keys_to_del:
            del self._store[k]
        logger.info("cache_invalidated_metrics", count=len(keys_to_del))
        return len(keys_to_del)

    async def invalidate_notifications(self) -> int:
        """Invalidates all cache keys prefixed with 'notifications:'."""
        keys_to_del = [k for k in self._store if k.startswith("notifications:")]
        for k in keys_to_del:
            del self._store[k]
        logger.info("cache_invalidated_notifications", count=len(keys_to_del))
        return len(keys_to_del)


# Backwards compatibility alias
DashboardCache = DashboardCacheService
