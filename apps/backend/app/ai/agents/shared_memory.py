import os
import json
from typing import Any, Dict, Optional, List
from app.ai.agents.interfaces import ISharedAgentMemory
from app.ai.agents.models import SharedMemoryItem


class SharedAgentMemory(ISharedAgentMemory):
    """Stores cross-agent context, mission memory, workspace context, and reusable patterns with persistent storage."""

    def __init__(self, storage_path: str = ".nova/shared_memory.json") -> None:
        self.storage_path = storage_path
        self._store: Dict[str, SharedMemoryItem] = {}
        self.load()

    def load(self) -> None:
        """Loads memory items from local persistent storage."""
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    self._store[k] = SharedMemoryItem(
                        key=v.get("key", k),
                        value=v.get("value"),
                        author=v.get("author", "system"),
                        category=v.get("category", "general"),
                    )
        except Exception:
            pass

    def save(self) -> None:
        """Saves current memory items to local persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)
            data = {}
            for k, item in self._store.items():
                data[k] = {
                    "key": item.key,
                    "value": item.value,
                    "author": item.author,
                    "category": item.category,
                }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def store(self, key: str, value: Any, author: str, category: str = "general") -> None:
        """Stores item in shared agent memory and persists to disk."""
        item = SharedMemoryItem(key=key, value=value, author=author, category=category)
        self._store[key] = item
        self.save()

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieves item from shared agent memory."""
        item = self._store.get(key)
        return item.value if item else None

    def list_keys(self) -> List[str]:
        return list(self._store.keys())

    def clear(self) -> None:
        """Clears memory items and removes storage file."""
        self._store.clear()
        if os.path.exists(self.storage_path):
            try:
                os.remove(self.storage_path)
            except Exception:
                pass

