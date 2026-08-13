"""Continuous Project Memory for Retaining Architecture Decisions and Bug History.
"""

from typing import Any, Dict, List
from app.ai.software_company.interfaces import IContinuousProjectMemory
from app.ai.software_company.models import ProjectMemoryItem


class ContinuousProjectMemory(IContinuousProjectMemory):
    """Remembers architecture decisions, bug history, deployment history, coding guidelines, and version records."""

    def __init__(self) -> None:
        self._memory_store: List[ProjectMemoryItem] = []

    def store_memory(self, project_id: str, category: str, content: Any) -> ProjectMemoryItem:
        """Stores project memory item."""
        item = ProjectMemoryItem(
            project_id=project_id,
            category=category,
            content=content,
        )
        self._memory_store.append(item)
        return item

    def get_project_history(self, project_id: str) -> List[ProjectMemoryItem]:
        """Retrieves project history and architectural memory."""
        return [m for m in self._memory_store if m.project_id == project_id]
