"""Sprint Manager schedules sprints and monitors iteration progress.
"""

from datetime import datetime, timedelta
from typing import List
from app.agents.software_engineer.project_manager.interfaces import ISprintManager
from app.agents.software_engineer.project_manager.models import Sprint, Task

class LocalSprintManager(ISprintManager):
    """Calculates sprint backlogs and handles task planning allocations."""

    def plan_sprint(self, backlog: List[Task], duration_weeks: int, goal: str) -> Sprint:
        """Schedules tasks from a backlog list into a defined sprint iteration."""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=duration_weeks)

        # Allocate tasks to the sprint (up to capacity, say 5 tasks or all if small)
        sprint_tasks = backlog[:6]

        return Sprint(
            id=f"sprint-{int(start_date.timestamp())}",
            name=f"Sprint {datetime.utcnow().strftime('%Y-%W')}",
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            duration_weeks=duration_weeks,
            tasks=sprint_tasks,
            is_completed=False
        )

    def track_sprint_completion(self, sprint: Sprint) -> float:
        """Calculates percentage of task completion in a sprint."""
        if not sprint.tasks:
            sprint.is_completed = True
            return 100.0

        completed = sum(1 for t in sprint.tasks if t.status == "COMPLETED")
        percentage = (completed / len(sprint.tasks)) * 100.0
        
        if completed == len(sprint.tasks):
            sprint.is_completed = True

        return percentage
