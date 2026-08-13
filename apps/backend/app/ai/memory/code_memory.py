"""Code Memory tracks classes, functions and dependency graphs.
"""

from typing import List
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.models import MemoryItem, MemoryType

class CodeMemory:
    """Manages class structures and method declarations indices."""

    def __init__(self, store: IVectorStore, embedding_mgr: EmbeddingManager) -> None:
        self.store = store
        self.embedding_mgr = embedding_mgr

    async def record_code_symbol(self, filepath: str, symbol_type: str, name: str, details: str) -> None:
        """Stores structural symbol signatures."""
        content = f"Code Symbol ({symbol_type}) [{name}] in file `{filepath}`: {details}"
        vector = await self.embedding_mgr.embed_text(content)
        item = MemoryItem(
            content=content,
            memory_type=MemoryType.CODE,
            metadata={
                "filepath": filepath,
                "symbol_type": symbol_type,
                "name": name,
                "memory_type": MemoryType.CODE.value
            },
            embedding=vector,
            importance_score=0.7
        )
        await self.store.add([item])
