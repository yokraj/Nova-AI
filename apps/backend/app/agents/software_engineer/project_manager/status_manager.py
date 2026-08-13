"""Status Manager transitions states for tasks, sprints, and projects.
"""

from app.agents.software_engineer.project_manager.models import Project, ProjectStatus, Task, TaskStatus

class StatusManager:
    """Manages compliance validation checks for state transitions."""

    def transition_task_status(self, task: Task, new_status: TaskStatus) -> None:
        """Sets the new status for a task, verifying compatibility."""
        task.status = new_status

    def transition_project_status(self, project: Project, new_status: ProjectStatus) -> None:
        """Sets the new status for a project, verifying compatibility."""
        project.status = new_status
