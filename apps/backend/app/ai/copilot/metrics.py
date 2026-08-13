"""Telemetry and metrics collector for AI Software Copilot.
"""

import time
from app.ai.copilot.models import CopilotMetrics


class CopilotMetricsTracker:
    """Collects and aggregates copilot execution telemetry."""

    def __init__(self) -> None:
        self._projects = 0
        self._lines = 0
        self._bugs = 0
        self._tests = 0
        self._deployments = 0
        self._total_latency = 0.0

    def record_project_created(self, lines: int, latency_ms: float) -> None:
        """Records telemetry for newly created project."""
        self._projects += 1
        self._lines += lines
        self._total_latency += latency_ms

    def record_bug_fixed(self) -> None:
        """Increments bug fix count."""
        self._bugs += 1

    def record_tests_passed(self, count: int) -> None:
        """Increments passed test count."""
        self._tests += count

    def record_deployment(self) -> None:
        """Increments deployment count."""
        self._deployments += 1

    def get_metrics(self) -> CopilotMetrics:
        """Returns current CopilotMetrics snapshot."""
        avg_lat = (self._total_latency / self._projects) if self._projects > 0 else 0.0
        return CopilotMetrics(
            projects_created=self._projects,
            lines_generated=self._lines,
            bugs_fixed=self._bugs,
            tests_passed=self._tests,
            deployments_completed=self._deployments,
            average_latency_ms=avg_lat,
            timestamp=time.time(),
        )
