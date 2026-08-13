"""Implements prompts and generated code caches.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CachePayload(BaseModel):
    """Container holding single cache generation entry details."""

    prompt: str
    context_hash: str
    generated_content: str
    model: str
    timestamp: float


class GenerationCacheData(BaseModel):
    """Holds cache data state."""

    entries: Dict[str, CachePayload] = Field(default_factory=dict)


class GenerationCache:
    """Manages serialization of model calls outputs."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.data = GenerationCacheData()
        self.load()

    def _get_key(self, prompt: str, context_hash: str) -> str:
        raw = f"{prompt}:{context_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def load(self) -> None:
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.data = GenerationCacheData.model_validate(raw)
            except Exception:
                self.data = GenerationCacheData()

    def get(self, prompt: str, context_hash: str) -> Optional[str]:
        key = self._get_key(prompt, context_hash)
        entry = self.data.entries.get(key)
        if entry:
            return entry.generated_content
        return None

    def set(self, prompt: str, context_hash: str, content: str, model: str) -> None:
        key = self._get_key(prompt, context_hash)
        self.data.entries[key] = CachePayload(
            prompt=prompt,
            context_hash=context_hash,
            generated_content=content,
            model=model,
            timestamp=time.time(),
        )

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data.model_dump(), f, indent=2)
        except Exception:
            pass
