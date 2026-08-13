"""Dashboard Rate Limiter Module.

Implements sliding window rate limiting for per-IP, per-user, per-endpoint requests
with burst limit enforcement and usage reporting.
"""

from collections import deque
import time
from typing import Dict, Optional, Tuple
import structlog

from app.security.exceptions import RateLimitException

logger = structlog.get_logger(__name__)


class DashboardRateLimiter:
    """Sliding window rate limiter with per-IP, per-user, and per-endpoint tracking."""

    def __init__(self, max_requests_per_min: int = 120, burst_limit: int = 30) -> None:
        self.max_rate = max_requests_per_min
        self.burst_limit = burst_limit
        self._history: Dict[str, deque] = {}
        logger.info("dashboard_rate_limiter_initialized", max_rate=max_requests_per_min, burst_limit=burst_limit)

    def _cleanup(self, key: str, now: float, window_seconds: float = 60.0) -> None:
        """Evicts timestamps older than sliding window."""
        if key in self._history:
            history = self._history[key]
            cutoff = now - window_seconds
            while history and history[0] < cutoff:
                history.popleft()

    def allow_request(self, key: str, window_seconds: float = 60.0) -> bool:
        """Returns True if request key is within allowed rate and burst limits."""
        now = time.time()
        self._cleanup(key, now, window_seconds)

        history = self._history.get(key, deque())

        # 1. Burst limit check (last 1 second)
        burst_cutoff = now - 1.0
        burst_count = sum(1 for ts in history if ts >= burst_cutoff)
        if burst_count >= self.burst_limit:
            logger.warning("rate_limit_burst_exceeded", key=key, count=burst_count)
            return False

        # 2. Window rate check
        if len(history) >= self.max_rate:
            logger.warning("rate_limit_window_exceeded", key=key, count=len(history))
            return False

        return True

    def record_request(self, key: str) -> None:
        """Records a timestamped request event for key."""
        now = time.time()
        if key not in self._history:
            self._history[key] = deque()
        self._history[key].append(now)

    def current_usage(self, key: str, window_seconds: float = 60.0) -> Tuple[int, float]:
        """Returns (current_count, percentage_used) for key."""
        now = time.time()
        self._cleanup(key, now, window_seconds)
        history = self._history.get(key, deque())
        count = len(history)
        pct = (count / self.max_rate * 100.0) if self.max_rate > 0 else 0.0
        return count, round(pct, 2)

    def reset(self, key: Optional[str] = None) -> None:
        """Resets rate limit history for a specific key or globally."""
        if key:
            if key in self._history:
                del self._history[key]
        else:
            self._history.clear()
        logger.debug("rate_limiter_reset", key=key)
