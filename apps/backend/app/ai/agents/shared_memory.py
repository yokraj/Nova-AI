"""Shared Agent Memory for Cross-Agent Knowledge Exchange.
"""

from typing import Any, Dict, Optional
from app.ai.agents.interfaces import ISharedAgentMemory
from app.ai.agents.models import SharedMemoryItem


class SharedAgentMemory(ISharedAgentMemory):
    """Stores cross-agent context, mission memory, workspace context, and reusable patterns."""

    def __init__(self) -> None:
        self._store: Dict[str, SharedMemoryItem] = {}

    def store(self, key: str, value: Any, author: str, category: str = "general") -> None:
        """Stores item in shared agent memory."""
        item = SharedMemoryItem(key=key, value=value, author=author, category=category)
        self._store[key] = item

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieves item from shared agent memory."""
        item = self._store.get(key)
        return item.value if item else None

    def list_keys(self) -> List[str]:
        return list(self._store.keys())
