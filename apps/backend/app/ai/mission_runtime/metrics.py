"""Telemetry and performance metrics collector for Autonomous Mission Runtime Engine.
"""

import time
from app.ai.mission_runtime.models import MissionMetrics


class MissionMetricsTracker:
    """Collects and aggregates mission runtime telemetry."""

    def __init__(self) -> None:
        self._total = 0
        self._active = 0
        self._completed = 0
        self._failed = 0
        self._recoveries = 0
        self._total_duration = 0.0

    def record_mission_created(self) -> None:
        """Increments mission creation count."""
        self._total += 1
        self._active += 1

    def record_mission_completed(self, duration_seconds: float) -> None:
        """Records telemetry for completed mission."""
        self._active = max(0, self._active - 1)
        self._completed += 1
        self._total_duration += duration_seconds

    def record_mission_failed(self) -> None:
        """Records telemetry for failed mission."""
        self._active = max(0, self._active - 1)
        self._failed += 1

    def record_recovery_succeeded(self) -> None:
        """Increments recovery count."""
        self._recoveries += 1

    def get_metrics(self) -> MissionMetrics:
        """Returns current MissionMetrics snapshot."""
        avg_dur = (self._total_duration / self._completed) if self._completed > 0 else 0.0
        return MissionMetrics(
            total_missions=self._total,
            active_missions=self._active,
            completed_missions=self._completed,
            failed_missions=self._failed,
            recoveries_succeeded=self._recoveries,
            avg_duration_seconds=avg_dur,
            timestamp=time.time(),
        )
