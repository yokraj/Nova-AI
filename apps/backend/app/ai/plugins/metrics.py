"""Plugin Metrics Tracker collecting platform telemetry and KPIs."""

from app.ai.plugins.models import PluginMetrics


class PluginMetricsTracker:
    """Telemetry collector for plugin platform operations."""

    def __init__(self) -> None:
        self._total_installed: int = 0
        self._total_loaded: int = 0
        self._total_enabled: int = 0
        self._total_executions: int = 0
        self._successful_executions: int = 0
        self._failed_executions: int = 0
        self._total_duration: float = 0.0
        self._approvals_requested: int = 0
        self._approvals_granted: int = 0

    def record_execution(self, success: bool, duration: float) -> None:
        """Record execution outcome and duration."""
        self._total_executions += 1
        self._total_duration += duration
        if success:
            self._successful_executions += 1
        else:
            self._failed_executions += 1

    def record_approval(self, granted: bool) -> None:
        """Record approval request."""
        self._approvals_requested += 1
        if granted:
            self._approvals_granted += 1

    def update_counts(self, installed: int, loaded: int, enabled: int) -> None:
        """Update active plugin status counters."""
        self._total_installed = installed
        self._total_loaded = loaded
        self._total_enabled = enabled

    def snapshot(self) -> PluginMetrics:
        """Return snapshot of telemetry metrics."""
        success_rate = (
            round(self._successful_executions / self._total_executions, 4)
            if self._total_executions > 0
            else 0.0
        )
        avg_dur = (
            round(self._total_duration / self._total_executions, 4)
            if self._total_executions > 0
            else 0.0
        )
        return PluginMetrics(
            total_installed=self._total_installed,
            total_loaded=self._total_loaded,
            total_enabled=self._total_enabled,
            total_executions=self._total_executions,
            successful_executions=self._successful_executions,
            failed_executions=self._failed_executions,
            success_rate=success_rate,
            average_duration_seconds=avg_dur,
            approvals_requested=self._approvals_requested,
            approvals_granted=self._approvals_granted,
        )
