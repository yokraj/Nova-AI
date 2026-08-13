"""Context Engine Master Orchestrator Module.

Integrates Universal Intelligence Engine, Memory Engine, Vector Memory, Hybrid RAG,
Knowledge Graph, Code Intelligence, Decision Engine, Planner, Reasoner, and Conversation Engine.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.context_engine.config import ContextEngineConfig
from app.context_engine.repository import ContextEngineRepository
from app.context_engine.service import (
    ContextAssemblyService,
    CompressionService,
    RankingService,
    CacheService,
    StatisticsService,
)

logger = structlog.get_logger(__name__)


class ContextEngine:
    """Enterprise Master Context Assembly & Optimization Engine Orchestrator."""

    def __init__(
        self, session: Optional[AsyncSession] = None, config: Optional[ContextEngineConfig] = None
    ) -> None:
        self.session = session
        self.config = config or ContextEngineConfig()
        self.repository = ContextEngineRepository(session=session)

        # Services Initialization
        self.assembly_service = ContextAssemblyService(repository=self.repository)
        self.compression_service = CompressionService(repository=self.repository)
        self.ranking_service = RankingService(repository=self.repository)
        self.cache_service = CacheService(repository=self.repository)
        self.statistics_service = StatisticsService(repository=self.repository)

        logger.info("context_engine_master_initialized")
