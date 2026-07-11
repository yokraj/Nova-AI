"""HealthMonitor tracking heartbeat logs.
"""

from datetime import datetime, timezone
from typing import Any, Dict


class HealthMonitor:
    """Monitors service statuses, heartbeats, and alert thresholds."""

    def __init__(self) -> None:
        """Initializes HealthMonitor."""
        self._status: str = "healthy"
        self._last_heartbeat: datetime = datetime.now(timezone.utc)
        self._checks_count: int = 0

    def healthy(self) -> None:
        """Flags status as healthy."""
        self._status = "healthy"
        self.heartbeat()

    def degraded(self) -> None:
        """Flags status as degraded."""
        self._status = "degraded"
        self.heartbeat()

    def unhealthy(self) -> None:
        """Flags status as unhealthy."""
        self._status = "unhealthy"
        self.heartbeat()

    def heartbeat(self) -> None:
        """Updates last check heartbeat timestamp."""
        self._last_heartbeat = datetime.now(timezone.utc)
        self._checks_count += 1

    def last_check(self) -> datetime:
        """Gets the last recorded heartbeat timestamp.

        Returns:
            Datetime object of last heartbeat.
        """
        return self._last_heartbeat

    def get_status(self) -> Dict[str, Any]:
        """Exposes health metrics for the dashboard.

        Returns:
            Dictionary containing health parameters.
        """
        return {
            "status": self._status,
            "last_heartbeat": self._last_heartbeat.isoformat(),
            "checks_count": self._checks_count,
        }
