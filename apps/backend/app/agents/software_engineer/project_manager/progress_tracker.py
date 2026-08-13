"""Progress Tracker computes metrics for sprint velocity, task totals, and ETAs.
"""

from datetime import datetime, timedelta
from app.agents.software_engineer.project_manager.interfaces import IProgressTracker
from app.agents.software_engineer.project_manager.models import Progress, Project

class LocalProgressTracker(IProgressTracker):
    """Calculates completion ratios and remaining work hours for projects."""

    def calculate_progress(self, project: Project) -> Progress:
        """Processes project states to return active metrics."""
        total_tasks = 0
        completed = 0
        blocked = 0
        pending = 0
        remaining_hours = 0.0

        for epic in project.epics:
            for feature in epic.features:
                for task in feature.tasks:
                    total_tasks += 1
                    if task.status == "COMPLETED":
                        completed += 1
                    elif task.status == "BLOCKED":
                        blocked += 1
                        remaining_hours += task.estimate.total_hours
                    else:
                        pending += 1
                        remaining_hours += task.estimate.total_hours

        percentage = 0.0
        if total_tasks > 0:
            percentage = (completed / total_tasks) * 100.0

        eta = datetime.utcnow() + timedelta(hours=remaining_hours)

        progress = Progress(
            progress_percentage=percentage,
            completed_tasks=completed,
            pending_tasks=pending,
            blocked_tasks=blocked,
            total_tasks=total_tasks,
            velocity=8.5,  # mock velocity
            remaining_work_hours=remaining_hours,
            eta=eta
        )
        project.progress = progress
        return progress
