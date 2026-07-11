"""Profiler timing block durations.
"""

import time
from typing import Optional


class Profiler:
    """Measures execution duration and triggers alert callbacks for slow runs."""

    def __init__(self) -> None:
        """Initializes Profiler."""
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    def start(self) -> None:
        """Starts profiler execution timer."""
        self._start_time = time.time()
        self._end_time = None

    def stop(self) -> float:
        """Stops profiler execution timer.

        Returns:
            Elapsed seconds duration.
        """
        self._end_time = time.time()
        return self.elapsed()

    def elapsed(self) -> float:
        """Calculates elapsed duration.

        Returns:
            Elapsed duration in seconds.
        """
        if self._start_time is None:
            return 0.0
        end = self._end_time or time.time()
        return end - self._start_time

    def slow_execution_detection(self, threshold_seconds: float = 1.0) -> bool:
        """Checks if elapsed duration exceeded threshold limits.

        Args:
            threshold_seconds: Timeout threshold duration in seconds.

        Returns:
            True if elapsed duration is greater than threshold.
        """
        return self.elapsed() > threshold_seconds
