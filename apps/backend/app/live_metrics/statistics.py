"""Metrics Statistics & Diagnostics Module.

Tracks engine execution metrics, collection latencies, broadcast counts,
skipped updates due to rate limits or zero-deltas, and channel statistics.
"""

from typing import Any, Dict
import structlog

logger = structlog.get_logger(__name__)


class MetricsStatistics:
    """Telemetry performance statistics tracker for Live Metrics Engine."""

    def __init__(self) -> None:
        self.collection_count: int = 0
        self.broadcast_count: int = 0
        self.skipped_updates: int = 0
        self.total_collection_time_ms: float = 0.0
        self.total_publish_time_ms: float = 0.0
        self.channel_statistics: Dict[str, Dict[str, int]] = {}

        logger.info("metrics_statistics_initialized")

    def record_collection(self, duration_ms: float) -> None:
        """Records a completed metric collection cycle."""
        self.collection_count += 1
        self.total_collection_time_ms += duration_ms

    def record_broadcast(self, channel: str, duration_ms: float = 0.0) -> None:
        """Records a successful WebSocket channel broadcast."""
        self.broadcast_count += 1
        self.total_publish_time_ms += duration_ms

        if channel not in self.channel_statistics:
            self.channel_statistics[channel] = {"broadcasts": 0, "skipped": 0}
        self.channel_statistics[channel]["broadcasts"] += 1

    def record_skipped(self, channel: str) -> None:
        """Records a skipped broadcast (unchanged data or rate-limited)."""
        self.skipped_updates += 1
        if channel not in self.channel_statistics:
            self.channel_statistics[channel] = {"broadcasts": 0, "skipped": 0}
        self.channel_statistics[channel]["skipped"] += 1

    def get_summary(self, connected_clients: int = 0) -> Dict[str, Any]:
        """Returns diagnostic statistics summary dictionary."""
        avg_coll = (self.total_collection_time_ms / self.collection_count) if self.collection_count > 0 else 0.0
        avg_pub = (self.total_publish_time_ms / self.broadcast_count) if self.broadcast_count > 0 else 0.0

        return {
            "collection_count": self.collection_count,
            "broadcast_count": self.broadcast_count,
            "skipped_updates": self.skipped_updates,
            "average_collection_time_ms": round(avg_coll, 2),
            "average_publish_time_ms": round(avg_pub, 2),
            "connected_clients": connected_clients,
            "channel_statistics": self.channel_statistics,
        }

    def reset(self) -> None:
        """Resets all telemetry counters."""
        self.collection_count = 0
        self.broadcast_count = 0
        self.skipped_updates = 0
        self.total_collection_time_ms = 0.0
        self.total_publish_time_ms = 0.0
        self.channel_statistics.clear()
