"""Vector Engine Master Orchestrator Module.

Unifies EmbeddingEngine, VectorStore, VectorSearch, VectorIndexManager,
VectorOptimizer, VectorCache, and StatisticsTracker into a single master orchestrator.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.vector_memory.config import VectorConfig
from app.vector_memory.repository import VectorRepository
from app.vector_memory.service import (
    EmbeddingService,
    VectorSearchService,
    VectorIndexService,
    StatisticsService,
)

logger = structlog.get_logger(__name__)


class VectorEngine:
    """Enterprise Master Vector Database & Embedding Engine Orchestrator."""

    def __init__(self, session: Optional[AsyncSession] = None, config: Optional[VectorConfig] = None) -> None:
        self.session = session
        self.config = config or VectorConfig()
        self.repository = VectorRepository(session=session)
        
        # Services Initialization
        self.embedding_service = EmbeddingService(repository=self.repository)
        self.search_service = VectorSearchService(repository=self.repository)
        self.index_service = VectorIndexService(repository=self.repository)
        self.statistics_service = StatisticsService(repository=self.repository)

        logger.info("vector_engine_master_initialized", default_model=self.config.default_model)
