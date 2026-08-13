"""Nova AI Live Metrics Engine Package.

Provides high-performance continuous metric collection, change detection thresholds,
channel rate limiting, in-memory snapshot ring buffering, and real-time WebSocket
broadcasting for the Enterprise Dashboard.
"""

from app.live_metrics.buffer import MetricsBuffer
from app.live_metrics.change_detector import ChangeDetector
from app.live_metrics.config import LiveMetricsConfig
from app.live_metrics.engine import LiveMetricsEngine
from app.live_metrics.exceptions import (
    BufferOverflow,
    CollectorFailure,
    LiveMetricsError,
    MetricsCollectionError,
    MonitoringFailure,
    PublishError,
    RateLimitExceeded,
    SchedulerError,
    SnapshotError,
)
from app.live_metrics.publisher import MetricsPublisher
from app.live_metrics.rate_limiter import MetricsRateLimiter
from app.live_metrics.scheduler import MetricsScheduler
from app.live_metrics.snapshot import SnapshotManager
from app.live_metrics.statistics import MetricsStatistics

__all__ = [
    "LiveMetricsEngine",
    "MetricsScheduler",
    "MetricsPublisher",
    "ChangeDetector",
    "SnapshotManager",
    "MetricsBuffer",
    "MetricsRateLimiter",
    "MetricsStatistics",
    "LiveMetricsConfig",
    "LiveMetricsError",
    "MetricsCollectionError",
    "PublishError",
    "SchedulerError",
    "SnapshotError",
    "RateLimitExceeded",
    "BufferOverflow",
    "CollectorFailure",
    "MonitoringFailure",
]
