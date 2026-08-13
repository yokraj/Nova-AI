"""Caching layer for memory lookup caches and document hash files.
"""

import json
import os
from typing import Dict, Any, Optional

class MemoryCache:
    """Caches document parse hashes to skip redundant indexing cycles."""

    def __init__(self, storage_path: str = ".nova/cache/memory/") -> None:
        self.storage_path = storage_path
        self.cache_file = os.path.join(storage_path, "memory_cache.json")
        self.data: Dict[str, Any] = {
            "document_hashes": {},
            "embeddings": {}
        }
        self.load()

    def load(self) -> None:
        """Loads cached hashes from disk."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            pass

    def save(self) -> None:
        """Saves current state to file."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get_doc_hash(self, filepath: str) -> Optional[str]:
        """Returns cached file contents MD5 hash."""
        return self.data["document_hashes"].get(filepath)

    def cache_doc_hash(self, filepath: str, file_hash: str) -> None:
        """Stores a document MD5 hash value."""
        self.data["document_hashes"][filepath] = file_hash
        self.save()
