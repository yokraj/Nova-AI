"""Context Deduplicator Module.

Removes duplicate memories, documents, code snippets, summaries, graph nodes, and citations based on text fingerprints.
"""

import hashlib
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ContextDeduplicator:
    """Enterprise Content Fingerprint Deduplication Engine."""

    def __init__(self) -> None:
        logger.info("context_deduplicator_initialized")

    def deduplicate(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates candidate list using content SHA256 hashes."""
        deduped: List[Dict[str, Any]] = []
        seen_hashes: Set[str] = set()

        for item in candidates:
            content_str = item.get("content") or item.get("title") or str(item.get("id"))
            text_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                deduped.append(item)

        logger.info("deduplication_completed", original_count=len(candidates), deduped_count=len(deduped))
        return deduped
