"""Project Memory Module.

Stores and queries project-level architectural decisions, requirements, tasks, files, history, agents, and notes.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class ProjectMemoryManager:
    """Enterprise Project Architectural & Historical Memory Manager."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        logger.info("project_memory_manager_initialized")

    async def record_project_decision(
        self,
        project_name: str,
        title: str,
        decision_content: str,
        workspace: str = "Nova",
    ) -> Dict[str, Any]:
        """Records a major architectural decision or requirement for a project."""
        entry = await self.repository.create_entry(
            title=f"Project Decision [{project_name}]: {title}",
            content=decision_content,
            summary=decision_content[:120],
            memory_type="project",
            workspace=workspace,
            project=project_name,
            tags=["architecture", "decision", project_name],
        )
        logger.info("project_decision_recorded", project_name=project_name, title=title)
        return {"memory_id": entry.id, "project": project_name, "title": title}

    async def get_project_summary(self, project_name: str) -> Dict[str, Any]:
        """Aggregates architectural decisions and project memories."""
        entries = await self.repository.search_entries(project=project_name, limit=50)
        return {
            "project_name": project_name,
            "memory_count": len(entries),
            "memories": [
                {"id": e.id, "title": e.title, "summary": e.summary, "created_at": e.created_at.isoformat()}
                for e in entries
            ],
        }
