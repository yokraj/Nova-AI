"""Telemetry metrics collector for Universal Skills Marketplace & SDK.
"""

import time
from app.ai.skills.models import SkillMetrics


class SkillMetricsTracker:
    """Collects skill execution metrics, installs, updates, and latencies."""

    def __init__(self) -> None:
        self._executions = 0
        self._failures = 0
        self._installs = 0
        self._updates = 0
        self._total_latency = 0.0

    def record_execution(self, success: bool, latency_ms: float) -> None:
        """Records execution telemetry metrics."""
        self._executions += 1
        if not success:
            self._failures += 1
        self._total_latency += latency_ms

    def record_install(self) -> None:
        """Records skill installation."""
        self._installs += 1

    def get_metrics(self) -> SkillMetrics:
        """Returns current SkillMetrics snapshot."""
        avg_lat = (self._total_latency / self._executions) if self._executions > 0 else 0.0
        return SkillMetrics(
            executions=self._executions,
            failures=self._failures,
            installs=self._installs,
            updates=self._updates,
            avg_latency_ms=avg_lat,
            timestamp=time.time(),
        )
