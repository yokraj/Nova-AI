"""Implements local caching of compiled ASTs, symbol maps, and call graphs.
"""

import json
import os
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.agents.software_engineer.intelligence.interfaces import CacheProvider


class CachePayload(BaseModel):
    """Payload representing saved intelligence cache entries."""

    mtime: float
    size: int
    hash: str
    symbols: List[Dict[str, Any]] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[Dict[str, Any]] = Field(default_factory=list)
    complexity: Dict[str, Any] = Field(default_factory=dict)


class IntelligenceCacheData(BaseModel):
    """Overall container holding intelligence cache database state."""

    files: Dict[str, CachePayload] = Field(default_factory=dict)
    dependency_graph: Dict[str, Any] = Field(default_factory=dict)
    call_graph: Dict[str, Any] = Field(default_factory=dict)
    last_update: float = Field(0.0)


class FileSystemCacheProvider(CacheProvider):
    """Persists Code Intelligence metadata to local workspace folder."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.data = IntelligenceCacheData()
        self.load()

    def load(self) -> None:
        """Loads cached databases state from filesystem."""
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.data = IntelligenceCacheData.model_validate(raw)
            except Exception:
                # Corrupted cache, reset
                self.data = IntelligenceCacheData()

    def get(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Fetches cached payload dictionary for path.

        Args:
            file_path: Relative file path.

        Returns:
            Dict or None.
        """
        payload = self.data.files.get(file_path)
        if payload:
            return payload.model_dump()
        return None

    def set(self, file_path: str, value: Dict[str, Any]) -> None:
        """Registers analysis payloads for path.

        Args:
            file_path: Relative path.
            value: Analysis payloads dictionary.
        """
        self.data.files[file_path] = CachePayload.model_validate(value)

    def save(self) -> None:
        """Persists database state changes to disk."""
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        self.data.last_update = time.time()
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data.model_dump(), f, indent=2)
        except Exception:
            pass

    def clear(self) -> None:
        """Cleans and deletes the cache file."""
        self.data = IntelligenceCacheData()
        if os.path.exists(self.cache_file_path):
            try:
                os.remove(self.cache_file_path)
            except OSError:
                pass


from typing import List
