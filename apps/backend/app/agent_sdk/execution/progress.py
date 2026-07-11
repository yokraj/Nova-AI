"""ProgressTracker tracking progress percent and estimates remainings.
"""

import time


class ProgressTracker:
    """Tracks and calculates execution progress metrics and remainings estimates."""

    def __init__(self) -> None:
        """Initializes ProgressTracker."""
        self.total_steps: int = 100
        self.current_step: int = 0
        self.message: str = ""
        self.start_time: float = 0.0
        self.completed: bool = False

    def start(self, total_steps: int = 100) -> None:
        """Starts progress tracking scope.

        Args:
            total_steps: Total steps count goal.
        """
        self.total_steps = max(1, total_steps)
        self.current_step = 0
        self.start_time = time.time()
        self.completed = False

    def update(self, step: int, message: str = "") -> None:
        """Updates progress tracking state.

        Args:
            step: Step index reached.
            message: Dynamic message updates string.
        """
        self.current_step = min(step, self.total_steps)
        self.message = message

    def complete(self, message: str = "") -> None:
        """Completes tracking scope.

        Args:
            message: Completion message update.
        """
        self.current_step = self.total_steps
        self.message = message
        self.completed = True

    def percentage(self) -> float:
        """Calculates current percent completion ratio.

        Returns:
            Float value from 0.0 to 100.0.
        """
        return (self.current_step / self.total_steps) * 100.0

    def estimated_remaining(self) -> float:
        """Estimates remaining execution duration in seconds.

        Returns:
            Estimated float remaining seconds.
        """
        if self.completed or self.current_step == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        rate = elapsed / self.current_step
        remaining_steps = self.total_steps - self.current_step
        return rate * remaining_steps
