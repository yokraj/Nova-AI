"""Memory Manager Module.

Implements MemoryManager providing core Memory CRUD, pin/archive operations,
restoration, memory merging, and memory splitting.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryEntryCreate, MemoryEntryUpdate, MemoryEntryResponse
from app.memory.memory_scoring import MemoryScoringEngine
from app.memory.exceptions import MemoryNotFoundError

logger = structlog.get_logger(__name__)


class MemoryManager:
    """Enterprise Master Memory Entry Lifecycle Manager."""

    def __init__(
        self,
        repository: MemoryRepository,
        scoring_engine: Optional[MemoryScoringEngine] = None,
    ) -> None:
        self.repository = repository
        self.scoring_engine = scoring_engine or MemoryScoringEngine()
        logger.info("memory_manager_initialized")

    async def create_memory(self, schema: MemoryEntryCreate) -> MemoryEntryResponse:
        """Creates a new memory entry."""
        entry = await self.repository.create_entry(
            title=schema.title,
            content=schema.content,
            summary=schema.summary,
            memory_type=schema.memory_type.value if hasattr(schema.memory_type, "value") else schema.memory_type,
            workspace=schema.workspace,
            project=schema.project,
            user_id=schema.user_id,
            importance=schema.importance,
            confidence=schema.confidence,
            is_pinned=schema.is_pinned,
            expires_at=schema.expires_at,
            tags=schema.tags,
            metadata_json=schema.metadata,
        )
        return self._to_response(entry)

    async def update_memory(self, memory_id: str, schema: MemoryEntryUpdate) -> MemoryEntryResponse:
        """Updates fields of an existing memory entry."""
        kwargs = schema.model_dump(exclude_unset=True)
        if "memory_type" in kwargs and hasattr(kwargs["memory_type"], "value"):
            kwargs["memory_type"] = kwargs["memory_type"].value

        entry = await self.repository.update_entry(memory_id, **kwargs)
        return self._to_response(entry)

    async def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory entry."""
        return await self.repository.delete_entry(memory_id)

    async def archive_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Archives a memory entry."""
        entry = await self.repository.update_entry(memory_id, is_archived=True)
        return self._to_response(entry)

    async def pin_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Pins a memory entry to prevent automatic expiration/archival."""
        entry = await self.repository.update_entry(memory_id, is_pinned=True)
        return self._to_response(entry)

    async def restore_memory(self, memory_id: str) -> MemoryEntryResponse:
        """Restores an archived memory entry."""
        entry = await self.repository.update_entry(memory_id, is_archived=False)
        return self._to_response(entry)

    async def merge_memories(self, source_ids: List[str], target_title: str) -> MemoryEntryResponse:
        """Merges multiple memory entries into a consolidated target memory."""
        contents: List[str] = []
        tags_set: List[str] = []

        for sid in source_ids:
            e = await self.repository.get_entry_by_id(sid)
            if e:
                contents.append(e.content)
                for t in e.tags:
                    if t.tag_name not in tags_set:
                        tags_set.append(t.tag_name)
                # Archive merged source
                await self.repository.update_entry(sid, is_archived=True)

        merged_content = "\n\n--- Merged Memory Content ---\n\n".join(contents)
        new_entry = await self.repository.create_entry(
            title=target_title,
            content=merged_content,
            summary=f"Merged from {len(source_ids)} source memories.",
            memory_type="long_term",
            tags=tags_set,
        )

        logger.info("memories_merged", source_count=len(source_ids), merged_id=new_entry.id)
        return self._to_response(new_entry)

    async def split_memory(self, memory_id: str, split_points: List[str]) -> List[MemoryEntryResponse]:
        """Splits a large memory entry into smaller memory chunks."""
        parent = await self.repository.get_entry_by_id(memory_id)
        if not parent:
            raise MemoryNotFoundError(f"Memory '{memory_id}' not found for splitting.")

        created_responses: List[MemoryEntryResponse] = []
        for idx, point_text in enumerate(split_points):
            child_title = f"{parent.title} [Part {idx + 1}]"
            c_entry = await self.repository.create_entry(
                title=child_title,
                content=point_text,
                summary=point_text[:100],
                memory_type=parent.memory_type,
                workspace=parent.workspace,
                project=parent.project,
            )
            # Create relationship link: child belongs_to parent
            await self.repository.create_relationship(
                source_id=c_entry.id,
                target_id=parent.id,
                relationship_type="belongs_to",
            )
            created_responses.append(self._to_response(c_entry))

        logger.info("memory_split_completed", parent_id=memory_id, parts=len(split_points))
        return created_responses

    def _to_response(self, entry: Any) -> MemoryEntryResponse:
        """Converts ORM model to Response DTO."""
        tags = [t.tag_name for t in entry.tags] if hasattr(entry, "tags") and entry.tags else []
        calculated_score = self.scoring_engine.calculate_priority_score(
            importance=entry.importance,
            created_at=entry.created_at,
            access_count=entry.access_count,
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
