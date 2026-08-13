"""Caching helper for the Project Manager Engine.
"""

import json
import os
from typing import Any, Dict, Optional

class ProjectManagerCache:
    """Manages simple file-based caching for project management tasks."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root
        self.cache_dir = os.path.join(workspace_root, ".nova") if workspace_root else None
        self.cache_file = os.path.join(self.cache_dir, "project_manager_cache.json") if self.cache_dir else None
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Loads cache data from file."""
        if not self.cache_file or not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}

    def save(self) -> None:
        """Saves current cache state."""
        if not self.cache_file or not self.cache_dir:
            return
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str) -> Optional[Any]:
        """Gets value from cache."""
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Sets value in cache and saves."""
        self.data[key] = value
        self.save()
