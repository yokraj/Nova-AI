"""Mission metrics collector tracking execution times and rates.
"""

from typing import Dict, Any, List

class MissionMetricsTracker:
    """Telemetry collector compiling completed/failed/recovered metrics counts."""

    def __init__(self) -> None:
        self.durations: List[float] = []
        self.completed_count = 0
        self.failed_count = 0
        self.retry_count = 0
        self.recovery_count = 0
        self.decisions_count = 0

    def record_duration(self, ms: float) -> None:
        """Logs mission execution duration."""
        self.durations.append(ms)

    def record_outcome(self, success: bool) -> None:
        """Increments outcome counters."""
        if success:
            self.completed_count += 1
        else:
            self.failed_count += 1

    def record_retry(self) -> None:
        """Increments retries counter."""
        self.retry_count += 1

    def record_recovery(self) -> None:
        """Increments recoveries counter."""
        self.recovery_count += 1

    def record_decision(self) -> None:
        """Increments decisions counter."""
        self.decisions_count += 1

    def dump_summary(self) -> Dict[str, Any]:
        """Returns metrics summary dictionary."""
        avg_dur = sum(self.durations) / len(self.durations) if self.durations else 0.0
        return {
            "avg_duration_ms": avg_dur,
            "completed_missions": self.completed_count,
            "failed_missions": self.failed_count,
            "total_retries": self.retry_count,
            "total_recoveries": self.recovery_count,
            "autonomous_decisions": self.decisions_count
        }
