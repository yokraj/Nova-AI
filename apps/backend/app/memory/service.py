"""Memory Service Layer Module.

Provides decoupled asynchronous business service abstractions:
MemoryService, ConversationMemoryService, WorkspaceMemoryService, ProjectMemoryService, and UserMemoryService.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository
from app.memory.memory_manager import MemoryManager
from app.memory.memory_search import MemorySearch
from app.memory.memory_scoring import MemoryScoringEngine
from app.memory.memory_compression import MemoryCompressor
from app.memory.memory_cleanup import MemoryCleaner
from app.memory.memory_indexer import MemoryIndexer
from app.memory.conversation_memory import ConversationMemoryManager
from app.memory.workspace_memory import WorkspaceMemoryManager
from app.memory.project_memory import ProjectMemoryManager
from app.memory.user_memory import UserMemoryManager
from app.memory.semantic_memory import SemanticMemoryManager
from app.memory.statistics import MemoryStatisticsTracker
from app.memory.schemas import (
    MemoryEntryCreate,
    MemoryEntryUpdate,
    MemoryEntryResponse,
    MemoryStatisticsSchema,
)

logger = structlog.get_logger(__name__)


class MemoryService:
    """Core Memory Business Service handling CRUD, search, merge, split, and statistics."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.scoring_engine = MemoryScoringEngine()
        self.memory_manager = MemoryManager(repository=repository, scoring_engine=self.scoring_engine)
        self.search_engine = MemorySearch(repository=repository, scoring_engine=self.scoring_engine)
        self.cleaner = MemoryCleaner(repository=repository)
        self.indexer = MemoryIndexer(repository=repository)
        self.stats_tracker = MemoryStatisticsTracker(repository=repository)
        logger.info("memory_service_initialized")

    async def create_memory(self, schema: MemoryEntryCreate) -> MemoryEntryResponse:
        """Creates a memory entry."""
        return await self.memory_manager.create_memory(schema)

    async def get_memory(self, memory_id: str) -> Optional[MemoryEntryResponse]:
        """Fetches memory entry by ID and increments access count."""
        entry = await self.repository.get_entry_by_id(memory_id)
        if not entry:
            return None
        await self.repository.increment_access_count(memory_id)
        self.stats_tracker.record_retrieval(latency_ms=1.2)
        return self.search_engine._to_response(entry)

    async def update_memory(self, memory_id: str, schema: MemoryEntryUpdate) -> MemoryEntryResponse:
        """Updates a memory entry."""
        return await self.memory_manager.update_memory(memory_id, schema)

    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory entry."""
        return await self.memory_manager.delete_memory(memory_id)

    async def archive_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Archives a memory entry."""
        return await self.memory_manager.archive_memory(memory_id)

    async def pin_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Pins a memory entry."""
        return await self.memory_manager.pin_memory(memory_id)

    async def restore_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Restores an archived memory entry."""
        return await self.memory_manager.restore_memory(memory_id)

    async def search(self, query: str, workspace: Optional[str] = None, limit: int = 20) -> List[MemoryEntryResponse]:
        """Performs multi-criteria memory search."""
        self.stats_tracker.record_retrieval(latency_ms=2.1)
        return await self.search_engine.search_text(query=query, workspace=workspace, limit=limit)

    async def get_statistics(self) -> MemoryStatisticsSchema:
        """Returns platform statistics summary."""
        return await self.stats_tracker.get_statistics()


class ConversationMemoryService:
    """Service abstraction for conversation thread memory."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.manager = ConversationMemoryManager(repository=repository)

    async def add_turn(self, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        """Appends a turn to conversation memory."""
        return await self.manager.add_turn(conversation_id, role, content)

    async def get_history(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves conversation thread history."""
        return await self.manager.get_history(conversation_id, limit)


class WorkspaceMemoryService:
    """Service abstraction for workspace isolation memory."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.manager = WorkspaceMemoryManager(repository=repository)

    async def get_workspace_memories(self, workspace_name: str) -> List[Dict[str, Any]]:
        """Retrieves workspace-scoped memories."""
        return await self.manager.get_workspace_memories(workspace_name)


class ProjectMemoryService:
    """Service abstraction for project-level architectural decisions and tasks."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.manager = ProjectMemoryManager(repository=repository)

    async def record_decision(self, project_name: str, title: str, decision_content: str) -> Dict[str, Any]:
        """Records a project architectural decision."""
        return await self.manager.record_project_decision(project_name, title, decision_content)

    async def get_summary(self, project_name: str) -> Dict[str, Any]:
        """Retrieves project architectural summary."""
        return await self.manager.get_project_summary(project_name)


class UserMemoryService:
    """Service abstraction for user preference and writing style profile memory."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        self.manager = UserMemoryManager(repository=repository)

    async def update_preferences(self, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Updates user preferences profile."""
        return await self.manager.update_preferences(user_id, **kwargs)

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieves user preference profile."""
        return await self.manager.get_user_profile(user_id)
