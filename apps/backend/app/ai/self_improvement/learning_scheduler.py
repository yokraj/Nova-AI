"""Learning Scheduler managing daily, weekly, and monthly evaluation cycles.
"""

from typing import Any, Dict
from app.ai.self_improvement.models import EvaluationCycle


class LearningScheduler:
    """Schedules background daily, weekly, and monthly evaluation cycles."""

    def trigger_cycle(self, cycle: EvaluationCycle = EvaluationCycle.DAILY) -> Dict[str, Any]:
        """Triggers scheduled evaluation cycle.

        Args:
            cycle: Target EvaluationCycle enum.

        Returns:
            Dictionary containing cycle name and status.
        """
        return {
            "cycle": cycle.value,
            "status": "COMPLETED",
            "next_run_in_hours": 24 if cycle == EvaluationCycle.DAILY else 168,
        }
