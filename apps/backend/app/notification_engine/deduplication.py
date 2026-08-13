"""Notification Deduplicator Module.

Prevents notification storms via time-window fingerprint hashing, message similarity
hashing, and automatic expiration cleanup.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class NotificationDeduplicator:
    """Time-window hash & similarity deduplicator for notifications."""

    def __init__(self, window_seconds: float = 300.0) -> None:
        self.window_seconds = window_seconds
        self._seen_hashes: Dict[str, float] = {}
        logger.info("notification_deduplicator_initialized", window_seconds=window_seconds)

    def _generate_fingerprint(self, payload: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 fingerprint hash for notification payload."""
        # Key fields for uniqueness identification
        title = (payload.get("title") or "").strip().lower()
        category = (payload.get("category") or "").strip().lower()
        message = (payload.get("message") or "").strip().lower()
        component = (payload.get("component") or "").strip().lower()

        normalized = f"{category}:{component}:{title}:{message[:50]}"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def is_duplicate(self, payload: Dict[str, Any]) -> bool:
        """Returns True if identical notification was registered within window_seconds."""
        now = time.time()
        self.cleanup(now)

        fingerprint = self._generate_fingerprint(payload)
        last_seen = self._seen_hashes.get(fingerprint)

        if last_seen and (now - last_seen) < self.window_seconds:
            logger.info("duplicate_notification_detected", fingerprint=fingerprint[:8], age_sec=round(now - last_seen, 2))
            return True

        return False

    def register(self, payload: Dict[str, Any]) -> str:
        """Registers notification fingerprint with current timestamp."""
        now = time.time()
        fingerprint = self._generate_fingerprint(payload)
        self._seen_hashes[fingerprint] = now
        return fingerprint

    def cleanup(self, current_time: Optional[float] = None) -> int:
        """Evicts expired fingerprint records older than window_seconds."""
        now = current_time or time.time()
        cutoff = now - self.window_seconds
        expired = [h for h, ts in self._seen_hashes.items() if ts < cutoff]

        for h in expired:
            del self._seen_hashes[h]

        if expired:
            logger.debug("deduplicator_cleaned_up_expired_records", count=len(expired))
        return len(expired)

    def clear(self) -> None:
        """Clears all fingerprint history."""
        self._seen_hashes.clear()
