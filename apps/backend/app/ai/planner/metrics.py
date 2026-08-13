"""Metrics tracker capturing performance timings for planning stages.
"""

import time
from typing import Dict

class PlannerMetricsTracker:
    """Computes elapsed durations for planner pipeline executions."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Resets stopwatch timestamps."""
        self._start_times: Dict[str, float] = {}
        self.latencies: Dict[str, float] = {}

    def start_stage(self, stage: str) -> None:
        """Starts timing tracking on target label."""
        self._start_times[stage] = time.perf_counter()

    def end_stage(self, stage: str) -> None:
        """Saves duration in milliseconds."""
        if stage in self._start_times:
            duration = (time.perf_counter() - self._start_times[stage]) * 1000.0
            self.latencies[stage] = duration
