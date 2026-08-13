"""Metrics Rate Limiter Module.

Enforces per-channel update rate limits, sliding window token limits,
and burst control to prevent network congestion across WebSocket streams.
"""

from collections import deque
import time
from typing import Dict
import structlog

logger = structlog.get_logger(__name__)


class MetricsRateLimiter:
    """Sliding-window per-channel rate limiter with burst control."""

    def __init__(self, max_rate_per_sec: float = 10.0, window_seconds: float = 1.0) -> None:
        self.max_rate = max_rate_per_sec
        self.window = window_seconds
        self._history: Dict[str, deque] = {}
        logger.info("metrics_rate_limiter_initialized", max_rate=max_rate_per_sec, window=window_seconds)

    def _cleanup_old_timestamps(self, channel: str, now: float) -> None:
        """Evicts timestamps older than sliding window."""
        if channel in self._history:
            history = self._history[channel]
            cutoff = now - self.window
            while history and history[0] < cutoff:
                history.popleft()

    def allow_publish(self, channel: str) -> bool:
        """Returns True if broadcasting on channel is within rate limit."""
        now = time.time()
        self._cleanup_old_timestamps(channel, now)

        history = self._history.get(channel, deque())
        if len(history) < int(self.max_rate * self.window):
            return True

        logger.debug("rate_limit_exceeded_for_channel", channel=channel, current_count=len(history))
        return False

    def record_publish(self, channel: str) -> None:
        """Records a successful publish event for channel."""
        now = time.time()
        if channel not in self._history:
            self._history[channel] = deque()
        self._history[channel].append(now)

    def current_rate(self, channel: str) -> float:
        """Calculates current updates/sec rate for channel."""
        now = time.time()
        self._cleanup_old_timestamps(channel, now)
        history = self._history.get(channel, deque())
        return len(history) / self.window if self.window > 0 else 0.0

    def reset(self) -> None:
        """Resets all channel rate history counters."""
        self._history.clear()
        logger.debug("metrics_rate_limiter_reset")
