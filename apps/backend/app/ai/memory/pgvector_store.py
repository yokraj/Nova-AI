"""PostgreSQL pgvector Vector Store adapter.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import delete as sql_delete
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.models import MemoryItem, RetrievalResult, MemoryType
from app.database.models.memory_model import MemoryModel
from app.database.session import SessionLocal
from app.ai.memory.exceptions import VectorStoreError

class PGVectorStore(IVectorStore):
    """Adapts SQLAlchemy and pgvector to retrieve and store vectors in PostgreSQL."""

    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or SessionLocal

    async def add(self, items: List[MemoryItem]) -> None:
        """Saves memory nodes and vector values to the database."""
        async with self.session_factory() as session:
            try:
                for item in items:
                    model = MemoryModel(
                        id=item.id,
                        content=item.content,
                        memory_type=item.memory_type.value,
                        metadata_json=item.metadata,
                        importance_score=item.importance_score,
                        embedding=item.embedding,
                        created_at=item.created_at
                    )
                    session.add(model)
                await session.commit()
            except Exception as err:
                await session.rollback()
                raise VectorStoreError(f"Failed to add items to PGVectorStore: {err}")

    async def search(self, query_vector: List[float], limit: int = 5, threshold: float = 0.7) -> List[RetrievalResult]:
        """Queries table for matches above cosine similarity thresholds."""
        async with self.session_factory() as session:
            try:
                # Retrieve all memories and perform cosine similarity locally or using pgvector
                # This ensures maximum compatibility regardless of whether the pgvector extension is compiled
                stmt = select(MemoryModel)
                result = await session.execute(stmt)
                models = result.scalars().all()

                results = []
                for m in models:
                    if not m.embedding:
                        continue
                    # Compute cosine similarity
                    import math
                    dot_product = sum(a * b for a, b in zip(query_vector, m.embedding))
                    norm_a = math.sqrt(sum(a * a for a in query_vector))
                    norm_b = math.sqrt(sum(b * b for b in m.embedding))
                    if norm_a == 0 or norm_b == 0:
                        similarity = 0.0
                    else:
                        similarity = dot_product / (norm_a * norm_b)

                    if similarity >= threshold:
                        results.append(
                            RetrievalResult(
                                memory_id=m.id,
                                content=m.content,
                                similarity_score=similarity,
                                source=m.metadata_json.get("source", "db"),
                                metadata=m.metadata_json
                            )
                        )

                # Sort by score descending and return top matches
                results.sort(key=lambda x: x.similarity_score, reverse=True)
                return results[:limit]
            except Exception as err:
                raise VectorStoreError(f"Failed to search PGVectorStore: {err}")

    async def delete(self, item_id: UUID) -> None:
        """Deletes database memory node by ID."""
        async with self.session_factory() as session:
            try:
                stmt = sql_delete(MemoryModel).where(MemoryModel.id == item_id)
                await session.execute(stmt)
                await session.commit()
            except Exception as err:
                await session.rollback()
                raise VectorStoreError(f"Failed to delete item: {err}")

    async def update(self, item: MemoryItem) -> None:
        """Updates record attributes."""
        async with self.session_factory() as session:
            try:
                stmt = select(MemoryModel).where(MemoryModel.id == item.id)
                result = await session.execute(stmt)
                model = result.scalars().first()
                if model:
                    model.content = item.content
                    model.metadata_json = item.metadata
                    model.importance_score = item.importance_score
                    if item.embedding:
                        model.embedding = item.embedding
                    await session.commit()
            except Exception as err:
                await session.rollback()
                raise VectorStoreError(f"Failed to update item: {err}")

    async def count(self) -> int:
        """Returns row count."""
        async with self.session_factory() as session:
            try:
                stmt = select(MemoryModel)
                result = await session.execute(stmt)
                return len(result.scalars().all())
            except Exception as err:
                raise VectorStoreError(f"Failed to count items: {err}")
