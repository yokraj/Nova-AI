"""Research Memory tracking historical sessions and supporting incremental research resumption.
"""

from typing import Dict, List, Optional
from app.ai.research.interfaces import IResearchMemory
from app.ai.research.models import ResearchMemoryItem


class ResearchMemory(IResearchMemory):
    """Stores past research sessions, enabling Nova to automatically resume prior research inquiries."""

    def __init__(self) -> None:
        self._memory_store: Dict[str, ResearchMemoryItem] = {}

    async def save_session(self, memory_item: ResearchMemoryItem) -> None:
        """Saves research session to memory dictionary.

        Args:
            memory_item: ResearchMemoryItem payload.
        """
        self._memory_store[memory_item.topic.lower()] = memory_item

    async def get_session(self, topic: str) -> Optional[ResearchMemoryItem]:
        """Retrieves past research session by topic string.

        Args:
            topic: Raw research query string.

        Returns:
            ResearchMemoryItem if found, else None.
        """
        return self._memory_store.get(topic.lower())

    async def list_history(self) -> List[ResearchMemoryItem]:
        """Returns list of all saved research session items."""
        return list(self._memory_store.values())
