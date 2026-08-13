"""Metrics tracker for visual pipeline telemetry.
"""

import time
import structlog
from typing import Dict, Any

logger = structlog.get_logger("vision_metrics")

class VisionMetricsTracker:
    """Telemetry collection helper for timing various visual pipeline stages."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Resets currently recorded metrics indicators."""
        self._start_time: Dict[str, float] = {}
        self._durations: Dict[str, float] = {}

    def start_stage(self, stage_name: str) -> None:
        """Starts a stopwatch for a pipeline stage."""
        self._start_time[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str) -> float:
        """Stops the stopwatch and records elapsed latency in milliseconds."""
        if stage_name not in self._start_time:
            return 0.0
        elapsed = (time.perf_counter() - self._start_time[stage_name]) * 1000.0
        self._durations[stage_name] = elapsed
        logger.debug("Vision pipeline stage finished", stage=stage_name, latency_ms=round(elapsed, 2))
        return elapsed

    def get_metrics(self) -> Dict[str, float]:
        """Returns the accumulated timing results."""
        return self._durations.copy()
