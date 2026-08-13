"""Milestone Manager tracks milestone creation, progress metrics, and completion.
"""

from typing import List, Dict
from app.agents.software_engineer.project_manager.models import Milestone, Task

class MilestoneManager:
    """Monitors completion ratios for planned roadmap milestones."""

    def update_milestone_status(self, milestone: Milestone, tasks: Dict[str, Task]) -> None:
        """Determines if a milestone is fully completed by examining assigned task states."""
        if not milestone.tasks:
            milestone.is_completed = True
            return

        completed_count = 0
        for tid in milestone.tasks:
            task = tasks.get(tid)
            if task and task.status == "COMPLETED":
                completed_count += 1

        milestone.is_completed = (completed_count == len(milestone.tasks))
