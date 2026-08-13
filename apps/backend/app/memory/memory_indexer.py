"""Memory Indexer Module.

Automatically ingests and indexes conversations, projects, files, code snippets,
documents, messages, notes, and task items into searchable memory entries and chunks.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class MemoryIndexer:
    """Enterprise Automated Indexer for System Artifacts & Communications."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        logger.info("memory_indexer_initialized")

    async def index_item(
        self,
        item_type: str,
        title: str,
        content: str,
        workspace: str = "Nova",
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Indexes an artifact item (code, doc, note, task, message) into persistent memory."""
        tags_list = tags or []
        if item_type not in tags_list:
            tags_list.append(item_type)

        entry = await self.repository.create_entry(
            title=title,
            content=content,
            summary=f"Indexed {item_type}: {title}",
            memory_type="knowledge" if item_type in ["code", "doc", "file"] else "long_term",
            workspace=workspace,
            project=project,
            tags=tags_list,
            metadata_json=metadata or {"item_type": item_type},
        )

        logger.info("item_indexed", item_type=item_type, title=title, memory_id=entry.id)
        return {
            "status": "indexed",
            "memory_id": entry.id,
            "item_type": item_type,
            "title": title,
        }
