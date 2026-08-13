"""Caching helper for routing decisions.
"""

import json
import os
from typing import Any, Dict, Optional

class RouterCache:
    """Saves previous routing choices to disk to optimize selection speeds."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()
        self.cache_dir = os.path.join(self.workspace_root, ".nova", "cache", "router")
        self.cache_file = os.path.join(self.cache_dir, "router_cache.json")
        self.data: Dict[str, Any] = {
            "decisions": {},
            "failures": {}
        }
        self.load()

    def load(self) -> None:
        """Loads cached decisions from file."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            pass

    def save(self) -> None:
        """Saves current state to cache file."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get_decision(self, prompt_hash: str) -> Optional[str]:
        """Returns cached model choice if available."""
        return self.data["decisions"].get(prompt_hash)

    def cache_decision(self, prompt_hash: str, model_name: str) -> None:
        """Stores model selection choice."""
        self.data["decisions"][prompt_hash] = model_name
        self.save()
