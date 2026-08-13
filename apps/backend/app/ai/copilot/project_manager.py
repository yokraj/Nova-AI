"""Project Manager memory store tracking project requirements, architecture, tasks, files, decisions, and risks.
"""

from typing import Any, Dict, Optional
from app.ai.copilot.interfaces import IProjectManager
from app.ai.copilot.models import ProjectState


class ProjectManager(IProjectManager):
    """In-memory project tracking store maintaining SDLC state."""

    def __init__(self) -> None:
        self._projects: Dict[str, ProjectState] = {}

    async def get_project(self, project_id: str) -> Optional[ProjectState]:
        """Retrieves project state by project_id or name."""
        if project_id in self._projects:
            return self._projects[project_id]
        for proj in self._projects.values():
            if proj.name.lower() == project_id.lower():
                return proj
        return None

    async def save_project(self, project: ProjectState) -> None:
        """Saves or updates project state."""
        self._projects[project.project_id] = project
        self._projects[project.name] = project

    def list_all_projects(self) -> List[ProjectState]:
        """Returns list of active projects."""
        return list({p.project_id: p for p in self._projects.values()}.values())
