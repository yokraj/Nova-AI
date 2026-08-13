"""Workflow metrics collector tracking latencies and failure counts.
"""

from typing import Dict, Any, List

class WorkflowMetricsTracker:
    """Tracks running workflow durations, total counts, retries, and checkpoint rates."""

    def __init__(self) -> None:
        self.durations: List[float] = []
        self.completed_count: int = 0
        self.failed_count: int = 0
        self.retry_count: int = 0
        self.rollback_count: int = 0
        self.approval_count: int = 0
        self.checkpoint_count: int = 0

    def record_duration(self, ms: float) -> None:
        """Logs completed workflow duration."""
        self.durations.append(ms)

    def record_outcome(self, success: bool) -> None:
        """Increments outcome counter."""
        if success:
            self.completed_count += 1
        else:
            self.failed_count += 1

    def record_retry(self) -> None:
        """Increments retries counter."""
        self.retry_count += 1

    def record_rollback(self) -> None:
        """Increments rollbacks counter."""
        self.rollback_count += 1

    def record_approval(self) -> None:
        """Increments approvals gate counter."""
        self.approval_count += 1

    def record_checkpoint(self) -> None:
        """Increments checkpoint saving counter."""
        self.checkpoint_count += 1

    def dump_summary(self) -> Dict[str, Any]:
        """Returns metrics summary dictionary."""
        avg_dur = sum(self.durations) / len(self.durations) if self.durations else 0.0
        return {
            "avg_duration_ms": avg_dur,
            "completed_workflows": self.completed_count,
            "failed_workflows": self.failed_count,
            "total_retries": self.retry_count,
            "total_rollbacks": self.rollback_count,
            "total_approvals": self.approval_count,
            "total_checkpoints": self.checkpoint_count
        }
