"""Progress Tracker calculating percentage completion for multi-step missions."""

from typing import Dict
from app.ai.execution.models import MissionExecutionPlan, StepStatus


class ProgressTracker:
    """Calculates completion percentages and progress indicators for missions."""

    def calculate_progress(self, plan: MissionExecutionPlan) -> float:
        """Compute percentage completion from step statuses."""
        if not plan.steps:
            return 100.0 if plan.state.value == "completed" else 0.0

        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        progress = round((completed / len(plan.steps)) * 100.0, 1)
        plan.progress_percentage = progress
        return progress

    def get_progress_summary(self, plan: MissionExecutionPlan) -> Dict[str, Any]:
        """Return structured progress breakdown."""
        progress = self.calculate_progress(plan)
        return {
            "mission_id": plan.mission_id,
            "goal": plan.goal,
            "state": plan.state.value,
            "progress_percentage": progress,
            "total_steps": len(plan.steps),
            "completed_steps": sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED),
            "failed_steps": sum(1 for s in plan.steps if s.status == StepStatus.FAILED),
        }


from typing import Any  # noqa: E402
