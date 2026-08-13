"""Mission Monitor tracking CPU, RAM, and agents active telemetry.
"""

from typing import Dict, Any

class MissionMonitor:
    """Collects hardware load metrics and workflow stats."""

    def __init__(self) -> None:
        self.failures_count = 0
        self.retry_count = 0

    def record_failure(self) -> None:
        """Increments failed steps metrics counts."""
        self.failures_count += 1

    def record_retry(self) -> None:
        """Increments retry counts."""
        self.retry_count += 1

    def collect_telemetry(self) -> Dict[str, Any]:
        """Gathers system metrics snapshots."""
        # Simulated resources limits offline
        return {
            "cpu_usage_pct": 12.5,
            "ram_usage_pct": 45.0,
            "failures_count": self.failures_count,
            "retry_count": self.retry_count,
            "idle_agents_count": 2
        }
