"""Workspace Memory Module.

Provides workspace isolation and workspace-scoped memory retrieval across domain partitions
(e.g., Nova, Marketplace, College, Research, Internship, Personal).
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class WorkspaceMemoryManager:
    """Enterprise Workspace Memory Scoping & Isolation Manager."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.supported_workspaces: List[str] = [
            "Nova",
            "Marketplace",
            "College",
            "Research",
            "Internship",
            "Personal",
        ]
        logger.info("workspace_memory_manager_initialized")

    async def get_workspace_memories(self, workspace_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves memories isolated strictly to target workspace partition."""
        entries = await self.repository.search_entries(workspace=workspace_name, limit=limit)
        return [
            {
                "id": e.id,
                "title": e.title,
                "summary": e.summary,
                "memory_type": e.memory_type,
                "workspace": e.workspace,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]
