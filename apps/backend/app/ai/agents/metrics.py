"""Performance metrics trackers tracking latency, error rates, and throughput.
"""

import time
from typing import Dict, Any

class AgentMetricsTracker:
    """Maintains atomic metrics counters and timings dictionaries."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Flushes execution statistics and timing histories."""
        self._start_times: Dict[str, float] = {}
        self.counts = {
            "registration_count": 0,
            "active_agents": 0,
            "failures": 0,
            "restart_count": 0,
            "event_throughput": 0
        }
        self.latencies = {
            "startup": 0.0,
            "execution": 0.0
        }

    def start_stage(self, stage: str) -> None:
        """Stores reference timestamp at transition initiation."""
        self._start_times[stage] = time.perf_counter()

    def end_stage(self, stage: str) -> None:
        """Updates millisecond duration metrics."""
        if stage in self._start_times:
            duration = (time.perf_counter() - self._start_times[stage]) * 1000.0
            self.latencies[stage] = duration

    def increment(self, metric: str) -> None:
        """Increments matching metric counter."""
        if metric in self.counts:
            self.counts[metric] += 1

    def decrement(self, metric: str) -> None:
        """Decrements matching metric counter."""
        if metric in self.counts:
            self.counts[metric] -= 1

    def get_metrics(self) -> Dict[str, Any]:
        """Exposes raw metrics telemetry dictionary."""
        return {
            "counts": self.counts,
            "latencies": self.latencies
        }
