"""Local Cache persisting generated documentation matched by prompt hashes.
"""

import json
import os
from typing import Dict, Optional


class DocumentationCache:
    """Manages serializing generated markdown summaries locally."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.entries: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception:
            pass

    def get(self, prompt_hash: str) -> Optional[dict]:
        return self.entries.get(prompt_hash)

    def set(self, prompt_hash: str, doc_data: dict) -> None:
        self.entries[prompt_hash] = doc_data
        self.save()
