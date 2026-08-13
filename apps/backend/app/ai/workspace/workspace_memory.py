"""Workspace Memory managing shared vector index and cross-member memory store.
"""

from typing import Any, Dict, List


class WorkspaceMemory:
    """Manages shared workspace vector memory and cross-member knowledge store."""

    def __init__(self) -> None:
        self._memory_store: List[Dict[str, Any]] = []

    def remember(self, workspace_id: str, key: str, value: Any) -> None:
        """Stores key-value memory entry for workspace."""
        self._memory_store.append({
            "workspace_id": workspace_id,
            "key": key,
            "value": value,
        })

    def search_memory(self, workspace_id: str, query: str) -> List[Dict[str, Any]]:
        """Searches memory store for matching entries."""
        return [m for m in self._memory_store if m["workspace_id"] == workspace_id]
