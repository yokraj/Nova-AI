"""Execution Metrics Tracker collecting execution KPIs and telemetry snapshots."""

from app.ai.execution.models import ExecutionMetrics


class ExecutionMetricsTracker:
    """Telemetry collector for execution runtime operations."""

    def __init__(self) -> None:
        self._total_missions: int = 0
        self._completed_missions: int = 0
        self._failed_missions: int = 0
        self._cancelled_missions: int = 0
        self._total_duration: float = 0.0
        self._total_steps: int = 0
        self._total_retries: int = 0
        self._total_rollbacks: int = 0
        self._approvals_requested: int = 0

    def record_mission_completion(self, success: bool, duration: float, steps_count: int) -> None:
        """Record mission outcome and duration."""
        self._total_missions += 1
        self._total_duration += duration
        self._total_steps += steps_count
        if success:
            self._completed_missions += 1
        else:
            self._failed_missions += 1

    def record_retry(self) -> None:
        """Record step retry."""
        self._total_retries += 1

    def record_rollback(self) -> None:
        """Record transaction rollback."""
        self._total_rollbacks += 1

    def record_approval_request(self) -> None:
        """Record human approval request."""
        self._approvals_requested += 1

    def snapshot(self) -> ExecutionMetrics:
        """Return telemetry metrics snapshot."""
        success_rate = (
            round(self._completed_missions / self._total_missions, 4)
            if self._total_missions > 0
            else 0.0
        )
        avg_dur = (
            round(self._total_duration / self._total_missions, 4)
            if self._total_missions > 0
            else 0.0
        )
        return ExecutionMetrics(
            total_missions=self._total_missions,
            completed_missions=self._completed_missions,
            failed_missions=self._failed_missions,
            cancelled_missions=self._cancelled_missions,
            success_rate=success_rate,
            average_mission_duration_seconds=avg_dur,
            total_steps_executed=self._total_steps,
            total_retries=self._total_retries,
            total_rollbacks=self._total_rollbacks,
            human_approvals_requested=self._approvals_requested,
        )
