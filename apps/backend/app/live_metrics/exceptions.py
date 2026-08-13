"""Live Metrics Engine Exceptions Module.

Defines domain exception classes for collection failures, rate limiting,
buffer overflows, snapshot diffing errors, and scheduler issues.
"""


class LiveMetricsError(Exception):
    """Base exception class for all Live Metrics Engine failures."""

    def __init__(self, message: str = "Live metrics error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class MetricsCollectionError(LiveMetricsError):
    """Raised when collecting metrics from hardware sensors fails."""

    def __init__(self, collector: str, detail: str) -> None:
        super().__init__(f"Metrics collection failed for '{collector}': {detail}")


class PublishError(LiveMetricsError):
    """Raised when broadcasting metric updates over WebSocket fails."""

    def __init__(self, channel: str, detail: str) -> None:
        super().__init__(f"Failed to publish metrics on channel '{channel}': {detail}")


class SchedulerError(LiveMetricsError):
    """Raised when background asyncio collection or cleanup task encounters unhandled failure."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Metrics scheduler error: {detail}")


class SnapshotError(LiveMetricsError):
    """Raised when snapshot capture, storage, or diffing fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Snapshot error: {detail}")


class RateLimitExceeded(LiveMetricsError):
    """Raised when channel update rate exceeds configured maximum publish rate."""

    def __init__(self, channel: str, rate: float) -> None:
        super().__init__(f"Rate limit exceeded on channel '{channel}': current rate {rate:.2f} updates/sec")


class BufferOverflow(LiveMetricsError):
    """Raised when metrics buffer reaches maximum capacity limit."""

    def __init__(self, capacity: int) -> None:
        super().__init__(f"Metrics buffer overflow: capacity limit {capacity} reached")


class CollectorFailure(LiveMetricsError):
    """Raised when an individual sensor collector component fails."""

    def __init__(self, collector_name: str, reason: str) -> None:
        super().__init__(f"Collector '{collector_name}' failed: {reason}")


class MonitoringFailure(LiveMetricsError):
    """Raised when system monitoring engine execution fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Monitoring engine failure: {detail}")
