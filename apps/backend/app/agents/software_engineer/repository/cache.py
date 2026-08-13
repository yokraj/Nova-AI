"""Implements filesystem caching for incremental scanning.
"""

import json
import os
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.agents.software_engineer.repository.interfaces import RepositoryCache


class CacheEntry(BaseModel):
    """File metadata stored in cache to detect modifications."""

    mtime: float = Field(..., description="Last modification timestamp.")
    size: int = Field(..., description="File size in bytes.")
    sha256: Optional[str] = Field(None, description="SHA256 checksum.")
    language: Optional[str] = Field(None, description="Detected language.")
    framework: Optional[str] = Field(None, description="Detected framework.")


class RepositoryCacheData(BaseModel):
    """Container holding all cache metadata."""

    scan_timestamp: float = Field(0.0)
    scan_duration: float = Field(0.0)
    files: Dict[str, CacheEntry] = Field(default_factory=dict)
    statistics: Optional[Dict[str, Any]] = Field(None)


class FileSystemRepositoryCache(RepositoryCache):
    """Serializes cache registry into a local JSON database."""

    def __init__(self, cache_file_path: str) -> None:
        """Initializes FileSystemRepositoryCache.

        Args:
            cache_file_path: Absolute path to cache JSON file.
        """
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.data = RepositoryCacheData()
        self.load()

    def load(self) -> Optional[RepositoryCacheData]:
        """Loads cached scan registry metadata.

        Returns:
            RepositoryCacheData model if successfully loaded, None otherwise.
        """
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self.data = RepositoryCacheData.model_validate(raw_data)
                    return self.data
            except Exception:
                # Corrupted cache file, reset and start fresh
                self.data = RepositoryCacheData()
        return None

    def save(self, scan_duration: float = 0.0) -> None:
        """Persists cache changes on disk.

        Args:
            scan_duration: Time duration of the scan.
        """
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        self.data.scan_timestamp = time.time()
        self.data.scan_duration = scan_duration
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data.model_dump(), f, indent=2)
        except Exception:
            pass

    def invalidate(self) -> None:
        """Cleans and deletes the cache file from disk."""
        self.data = RepositoryCacheData()
        if os.path.exists(self.cache_file_path):
            try:
                os.remove(self.cache_file_path)
            except OSError:
                pass

    def reload(self) -> None:
        """Reloads cache metadata from filesystem."""
        self.load()

    def get_entry(self, rel_path: str) -> Optional[CacheEntry]:
        """Fetches cache records for file relative path.

        Args:
            rel_path: Relative path of file.

        Returns:
            CacheEntry or None.
        """
        return self.data.files.get(rel_path)

    def set_entry(self, rel_path: str, entry: Any) -> None:
        """Registers a file signature entry on cache registry.

        Args:
            rel_path: Relative path of file.
            entry: CacheEntry to set.
        """
        self.data.files[rel_path] = entry


class RepositoryCacheDataWrapper:
    """Provides high-level actions mapping to underlying caching implementations."""

    # This wrapper can be used if any other component wants a clean state.
    pass
