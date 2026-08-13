"""Memory Cleanup Module.

Provides automated cleanup routines for purging expired temporary memories,
archived entry lifecycle maintenance, and storage capacity enforcement.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class MemoryCleaner:
    """Enterprise Memory Purge & Storage Lifecycle Manager."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        logger.info("memory_cleaner_initialized")

    async def purge_expired_memories(self) -> int:
        """Purges memories whose expires_at timestamp has passed."""
        now = datetime.now(timezone.utc)
        # Fetch entries to check expiration
        entries = await self.repository.search_entries(limit=1000)
        purged_count = 0

        for entry in entries:
            if entry.expires_at and entry.expires_at <= now and not entry.is_pinned:
                await self.repository.delete_entry(entry.id)
                purged_count += 1

        logger.info("expired_memories_purged", count=purged_count)
        return purged_count

    async def archive_old_unpinned(self, age_days: float = 30.0) -> int:
        """Archives unpinned memories older than specified age threshold."""
        now = datetime.now(timezone.utc)
        entries = await self.repository.search_entries(limit=1000)
        archived_count = 0

        for entry in entries:
            if not entry.is_pinned and not entry.is_archived:
                age = (now - entry.created_at).total_seconds() / 86400.0
                if age >= age_days:
                    await self.repository.update_entry(entry.id, is_archived=True)
                    archived_count += 1

        logger.info("old_memories_archived", count=archived_count)
        return archived_count
