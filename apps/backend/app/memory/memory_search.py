"""Memory Search Module.

Implements MemorySearch providing text search, workspace search, project search,
user search, tag search, relationship search, recency search, and importance search.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryEntryResponse
from app.memory.memory_scoring import MemoryScoringEngine

logger = structlog.get_logger(__name__)


class MemorySearch:
    """Enterprise Memory Multi-Criteria Search Engine."""

    def __init__(
        self,
        repository: MemoryRepository,
        scoring_engine: Optional[MemoryScoringEngine] = None,
    ) -> None:
        self.repository = repository
        self.scoring_engine = scoring_engine or MemoryScoringEngine()
        logger.info("memory_search_initialized")

    async def search_text(self, query: str, workspace: Optional[str] = None, limit: int = 20) -> List[MemoryEntryResponse]:
        """Searches memory entries by text query in title, content, or summary."""
        entries = await self.repository.search_entries(query=query, workspace=workspace, limit=limit)
        return [self._to_response(e, query_text=query) for e in entries]

    async def search_semantic(self, concept_query: str, limit: int = 20) -> List[MemoryEntryResponse]:
        """Performs concept-level semantic search across memory index."""
        # Simulated semantic text fallback
        return await self.search_text(query=concept_query, limit=limit)

    async def search_workspace(self, workspace: str, limit: int = 20) -> List[MemoryEntryResponse]:
        """Filters memories by workspace partition."""
        entries = await self.repository.search_entries(workspace=workspace, limit=limit)
        return [self._to_response(e) for e in entries]

    async def search_project(self, project: str, limit: int = 20) -> List[MemoryEntryResponse]:
        """Filters memories by project scope."""
        entries = await self.repository.search_entries(project=project, limit=limit)
        return [self._to_response(e) for e in entries]

    async def search_user(self, user_id: str, limit: int = 20) -> List[MemoryEntryResponse]:
        """Filters memories by owner user ID."""
        entries = await self.repository.search_entries(user_id=user_id, limit=limit)
        return [self._to_response(e) for e in entries]

    async def search_tags(self, tags: List[str], limit: int = 20) -> List[MemoryEntryResponse]:
        """Filters memories matching any of the specified tag labels."""
        all_entries = await self.repository.search_entries(limit=100)
        matched = []
        for e in all_entries:
            entry_tags = [t.tag_name for t in e.tags]
            if any(t in entry_tags for t in tags):
                matched.append(e)
        return [self._to_response(e) for e in matched[:limit]]

    async def search_relationships(self, memory_id: str) -> List[Dict[str, Any]]:
        """Retrieves relationship linkages connected to target memory ID."""
        entry = await self.repository.get_entry_by_id(memory_id)
        if not entry:
            return []

        rels = []
        for r in entry.source_relationships:
            rels.append({
                "relationship_id": r.id,
                "direction": "outgoing",
                "source_id": r.source_id,
                "target_id": r.target_id,
                "type": r.relationship_type,
                "weight": r.weight,
            })
        for r in entry.target_relationships:
            rels.append({
                "relationship_id": r.id,
                "direction": "incoming",
                "source_id": r.source_id,
                "target_id": r.target_id,
                "type": r.relationship_type,
                "weight": r.weight,
            })
        return rels

    async def search_recent(self, limit: int = 10) -> List[MemoryEntryResponse]:
        """Retrieves most recently created memory entries."""
        entries = await self.repository.search_entries(limit=limit)
        return [self._to_response(e) for e in entries]

    async def search_important(self, min_importance: float = 0.7, limit: int = 10) -> List[MemoryEntryResponse]:
        """Retrieves high-importance memory entries."""
        entries = await self.repository.search_entries(min_importance=min_importance, limit=limit)
        return [self._to_response(e) for e in entries]

    def _to_response(self, entry: Any, query_text: str = "") -> MemoryEntryResponse:
        """Converts ORM model to Pydantic Response DTO with calculated priority score."""
        tags = [t.tag_name for t in entry.tags] if hasattr(entry, "tags") and entry.tags else []
        relevance = 1.0 if not query_text or query_text.lower() in entry.title.lower() else 0.7
        calculated_score = self.scoring_engine.calculate_priority_score(
            importance=entry.importance,
            created_at=entry.created_at,
            access_count=entry.access_count,
            relevance=relevance,
            confidence=entry.confidence,
        )

        return MemoryEntryResponse(
            id=entry.id,
            title=entry.title,
            content=entry.content,
            summary=entry.summary,
            memory_type=entry.memory_type,
            workspace=entry.workspace,
            project=entry.project,
            user_id=entry.user_id,
            importance=entry.importance,
            confidence=entry.confidence,
            access_count=entry.access_count,
            is_pinned=entry.is_pinned,
            is_archived=entry.is_archived,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            expires_at=entry.expires_at,
            tags=tags,
            metadata=entry.metadata_json or {},
            calculated_score=calculated_score,
        )
