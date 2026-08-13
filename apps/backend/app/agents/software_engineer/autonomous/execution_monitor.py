"""Execution Monitor tracks active task steps timings.
"""

import time
from typing import Dict

class ExecutionMonitor:
    """Monitors durations to identify bottlenecks."""

    def __init__(self) -> None:
        self.timers: Dict[str, float] = {}

    def start_timer(self, step_id: str) -> None:
        """Starts timing tracking for a step."""
        self.timers[step_id] = time.perf_counter()

    def stop_timer(self, step_id: str) -> float:
        """Stops timing tracking and returns elapsed seconds."""
        start = self.timers.pop(step_id, None)
        if start is not None:
            return time.perf_counter() - start
        return 0.0
