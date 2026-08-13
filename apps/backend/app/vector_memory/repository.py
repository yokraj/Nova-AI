"""Vector Repository Module.

Provides asynchronous database access for embedding records, embedding jobs,
vector index metadata, and vector statistics, with fast fallback for testing environments.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.vector_memory.models import (
    EmbeddingModel,
    EmbeddingModelRegistry,
    EmbeddingJobModel,
    VectorIndexModel,
    VectorStatisticsModel,
)
from app.vector_memory.exceptions import VectorStoreError, VectorIndexNotFoundError

logger = structlog.get_logger(__name__)


class VectorRepository:
    """Enterprise Vector Database Repository."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self._in_memory_embeddings: Dict[str, EmbeddingModel] = {}

    async def save_embedding(
        self,
        memory_id: str,
        vector: List[float],
        model_name: str = "BAAI/bge-small-en-v1.5",
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> EmbeddingModel:
        """Saves or updates an embedding record."""
        emb_id = str(uuid.uuid4())
        record = EmbeddingModel(
            id=emb_id,
            memory_id=memory_id,
            model_name=model_name,
            dimension=len(vector),
            vector_json=vector,
            workspace=workspace,
            project=project,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._in_memory_embeddings[emb_id] = record

        if self.session is not None:
            try:
                self.session.add(record)
                await self.session.commit()
            except Exception:
                pass

        logger.info("embedding_saved", id=emb_id, memory_id=memory_id, dimension=len(vector))
        return record

    async def get_embedding(self, embedding_id: str) -> Optional[EmbeddingModel]:
        """Fetches embedding record by primary key ID."""
        if self.session is not None:
            try:
                stmt = select(EmbeddingModel).where(EmbeddingModel.id == embedding_id)
                res = await self.session.execute(stmt)
                item = res.scalar_one_or_none()
                if item:
                    return item
            except Exception:
                pass
        return self._in_memory_embeddings.get(embedding_id)

    async def delete_embedding(self, embedding_id: str) -> bool:
        """Deletes embedding record by ID."""
        if embedding_id in self._in_memory_embeddings:
            del self._in_memory_embeddings[embedding_id]

        if self.session is not None:
            try:
                stmt = delete(EmbeddingModel).where(EmbeddingModel.id == embedding_id)
                await self.session.execute(stmt)
                await self.session.commit()
            except Exception:
                pass

        logger.info("embedding_deleted", embedding_id=embedding_id)
        return True

    async def get_embeddings_count(self) -> int:
        """Returns total saved embedding record count."""
        if self.session is not None:
            try:
                count = await self.session.scalar(select(func.count(EmbeddingModel.id)))
                if count is not None:
                    return count
            except Exception:
                pass
        return len(self._in_memory_embeddings)
