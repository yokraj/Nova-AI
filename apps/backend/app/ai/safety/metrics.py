"""Safety metrics tracker recording rejections, policies counts, and timings.
"""

from typing import Dict, Any, List

class SafetyMetricsTracker:
    """Telemetry collector counting outcomes of approval gates."""

    def __init__(self) -> None:
        self.approvals_count = 0
        self.rejections_count = 0
        self.expired_count = 0
        self.violations_count = 0
        self.response_times: List[float] = []

    def record_outcome(self, approved: bool) -> None:
        """Increments resolved counters."""
        if approved:
            self.approvals_count += 1
        else:
            self.rejections_count += 1

    def record_expiration(self) -> None:
        """Increments expired items count."""
        self.expired_count += 1

    def record_violation(self) -> None:
        """Increments policy violation counter."""
        self.violations_count += 1

    def record_response_time(self, ms: float) -> None:
        """Appends response time metrics."""
        self.response_times.append(ms)

    def dump_summary(self) -> Dict[str, Any]:
        """Returns metrics summary dictionary."""
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        return {
            "total_approvals": self.approvals_count,
            "total_rejections": self.rejections_count,
            "expired_approvals": self.expired_count,
            "policy_violations": self.violations_count,
            "avg_response_time_ms": avg_time
        }
