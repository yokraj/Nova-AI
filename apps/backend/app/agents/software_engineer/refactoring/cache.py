"""Refactoring Cache persisting plans, prompts and generated patches.
"""

import hashlib
import json
import os
import time
from typing import Dict, Optional
from pydantic import BaseModel, Field


class RefactorCachePayload(BaseModel):
    """Payload of a cached refactoring execution run."""

    prompt: str
    context_hash: str
    output_code: str
    timestamp: float


class RefactorCacheData(BaseModel):
    """Holds all cached records mapping."""

    entries: Dict[str, RefactorCachePayload] = Field(default_factory=dict)


class RefactoringCache:
    """Manages JSON file caching for refactoring operations."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.data = RefactorCacheData()
        self.load()

    def _get_key(self, prompt: str, context_hash: str) -> str:
        raw = f"{prompt}:{context_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def load(self) -> None:
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.data = RefactorCacheData.model_validate(raw)
            except Exception:
                self.data = RefactorCacheData()

    def get(self, prompt: str, context_hash: str) -> Optional[str]:
        key = self._get_key(prompt, context_hash)
        entry = self.data.entries.get(key)
        if entry:
            return entry.output_code
        return None

    def set(self, prompt: str, context_hash: str, output: str) -> None:
        key = self._get_key(prompt, context_hash)
        self.data.entries[key] = RefactorCachePayload(
            prompt=prompt,
            context_hash=context_hash,
            output_code=output,
            timestamp=time.time(),
        )

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data.model_dump(), f, indent=2)
        except Exception:
            pass
