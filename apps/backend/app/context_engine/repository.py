"""Context Engine Repository Module.

Provides asynchronous database access for context build logs, cache records,
quality evaluation logs, and telemetry statistics.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.context_engine.models import (
    ContextBuildModel,
    ContextCacheModel,
    ContextQualityModel,
    ContextStatisticsModel,
)

logger = structlog.get_logger(__name__)


class ContextEngineRepository:
    """Enterprise Context Engine Database Repository."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self._in_memory_builds: Dict[str, ContextBuildModel] = {}

    async def save_build_log(
        self,
        query: str,
        token_budget: int,
        final_token_count: int,
        compression_ratio: float,
        quality_score: float,
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> ContextBuildModel:
        """Saves a context assembly build log."""
        build_id = str(uuid.uuid4())
        record = ContextBuildModel(
            id=build_id,
            query=query,
            workspace=workspace,
            project=project,
            token_budget=token_budget,
            final_token_count=final_token_count,
            compression_ratio=compression_ratio,
            quality_score=quality_score,
            created_at=datetime.now(timezone.utc),
        )

        self._in_memory_builds[build_id] = record

        if self.session is not None:
            try:
                self.session.add(record)
                await self.session.commit()
            except Exception:
                pass

        logger.info("context_build_logged", id=build_id, final_tokens=final_token_count, quality_score=quality_score)
        return record

    async def get_build_log(self, build_id: str) -> Optional[ContextBuildModel]:
        """Fetches build log by ID."""
        if self.session is not None:
            try:
                stmt = select(ContextBuildModel).where(ContextBuildModel.id == build_id)
                res = await self.session.execute(stmt)
                item = res.scalar_one_or_none()
                if item:
                    return item
            except Exception:
                pass
        return self._in_memory_builds.get(build_id)

    async def count_builds(self) -> int:
        """Returns total context assemblies count."""
        if self.session is not None:
            try:
                count = await self.session.scalar(select(func.count(ContextBuildModel.id)))
                if count is not None:
                    return count
            except Exception:
                pass
        return len(self._in_memory_builds)
