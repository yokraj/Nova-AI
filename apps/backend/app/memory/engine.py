"""Memory Engine Master Orchestrator Module.

Unifies MemoryService, ConversationMemoryService, WorkspaceMemoryService,
ProjectMemoryService, and UserMemoryService into a single entry point for Nova AI Operating System.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.config import MemoryConfig
from app.memory.repository import MemoryRepository
from app.memory.service import (
    MemoryService,
    ConversationMemoryService,
    WorkspaceMemoryService,
    ProjectMemoryService,
    UserMemoryService,
)

logger = structlog.get_logger(__name__)


class MemoryEngine:
    """Enterprise Master Memory Engine Orchestrator."""

    def __init__(self, session: AsyncSession, config: Optional[MemoryConfig] = None) -> None:
        self.session = session
        self.config = config or MemoryConfig()
        self.repository = MemoryRepository(session=session)
        
        # Sub-services Initialization
        self.memory_service = MemoryService(repository=self.repository)
        self.conversation_service = ConversationMemoryService(repository=self.repository)
        self.workspace_service = WorkspaceMemoryService(repository=self.repository)
        self.project_service = ProjectMemoryService(repository=self.repository)
        self.user_service = UserMemoryService(repository=self.repository)

        logger.info("memory_engine_master_initialized")
