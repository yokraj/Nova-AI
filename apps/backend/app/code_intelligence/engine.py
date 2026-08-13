"""Code Intelligence Engine Master Orchestrator Module.

Integrates Universal Intelligence Engine, Memory Engine, Vector Memory, Hybrid RAG,
Knowledge Graph, Decision Engine, Planner, and Reasoner.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.code_intelligence.config import CodeIntelligenceConfig
from app.code_intelligence.repository import CodeIntelligenceRepository
from app.code_intelligence.service import (
    RepositoryService,
    DocumentService,
    CodeAnalysisService,
    DependencyService,
    ArchitectureService,
    SummaryService,
)

logger = structlog.get_logger(__name__)


class CodeIntelligenceEngine:
    """Enterprise Master Document & Code Intelligence Engine Orchestrator."""

    def __init__(
        self, session: Optional[AsyncSession] = None, config: Optional[CodeIntelligenceConfig] = None
    ) -> None:
        self.session = session
        self.config = config or CodeIntelligenceConfig()
        self.repository = CodeIntelligenceRepository(session=session)

        # Services Initialization
        self.repository_service = RepositoryService(repository=self.repository)
        self.document_service = DocumentService(repository=self.repository)
        self.analysis_service = CodeAnalysisService(repository=self.repository)
        self.dependency_service = DependencyService(repository=self.repository)
        self.architecture_service = ArchitectureService(repository=self.repository)
        self.summary_service = SummaryService(repository=self.repository)

        logger.info("code_intelligence_engine_master_initialized")
