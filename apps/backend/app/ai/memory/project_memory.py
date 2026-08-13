"""Project Memory manages codebase tech selections and guidelines.
"""

from typing import List
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.models import MemoryItem, MemoryType

class ProjectMemory:
    """Manages index keys for architecture structures and development milestones."""

    def __init__(self, store: IVectorStore, embedding_mgr: EmbeddingManager) -> None:
        self.store = store
        self.embedding_mgr = embedding_mgr

    async def record_technology_choice(self, title: str, choice_description: str) -> None:
        """Stores technology stacked choices to project index memory."""
        content = f"Architecture Decision [{title}]: {choice_description}"
        vector = await self.embedding_mgr.embed_text(content)
        item = MemoryItem(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata={
                "title": title,
                "memory_type": MemoryType.PROJECT.value
            },
            embedding=vector,
            importance_score=0.9
        )
        await self.store.add([item])

    async def get_tech_stack_contexts(self) -> List[str]:
        """Returns stack info matching general tech stack query."""
        q_vec = await self.embedding_mgr.embed_text("project development technology choices framework database")
        results = await self.store.search(q_vec, limit=10, threshold=0.6)
        
        return [
            r.content for r in results if r.metadata.get("memory_type") == MemoryType.PROJECT.value
        ]
