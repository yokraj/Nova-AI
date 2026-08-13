"""Memory Manager tracks choices, code modifications, and syncs history.
"""

from typing import List
from app.agents.software_engineer.autonomous.interfaces import IMemoryManager
from app.agents.software_engineer.autonomous.models import MemoryEntry
from app.agents.software_engineer.documentation.knowledge_builder import LocalKnowledgeBuilder
from app.agents.software_engineer.documentation.knowledge_index import LocalKnowledgeIndexer
from app.agents.software_engineer.documentation.models import KnowledgeEntry

class LocalMemoryManager(IMemoryManager):
    """Stores past decisions and packages them for document builders."""

    def __init__(self) -> None:
        self.builder = LocalKnowledgeBuilder()
        self.indexer = LocalKnowledgeIndexer()
        self.history: List[MemoryEntry] = []

    def commit_memory(self, entry: MemoryEntry) -> None:
        """Saves a memory entry and indexes it inside the documentation knowledge base."""
        self.history.append(entry)

        # Sync with documentation KnowledgeBase
        ke = KnowledgeEntry(
            title=f"Autonomous Action - {entry.category}",
            content=entry.description,
            category="autonomous_history",
            timestamp=entry.timestamp.timestamp()
        )
        try:
            self.indexer.index_knowledge([ke])
        except Exception:
            pass

    def list_history(self) -> List[MemoryEntry]:
        """Lists tracked execution memory logs."""
        return self.history
