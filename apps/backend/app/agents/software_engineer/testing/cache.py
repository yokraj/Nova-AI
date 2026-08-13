"""Local Cache persisting coverage records and benchmarks outcomes.
"""

import hashlib
import json
import os
import time
from typing import Dict, Optional
from pydantic import BaseModel, Field


class TestCachePayload(BaseModel):
    """Payload representing a single cached verification run."""

    prompt: str
    context_hash: str
    result_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float


class TestCacheData(BaseModel):
    """Collection holding cache runs mappings."""

    entries: Dict[str, TestCachePayload] = Field(default_factory=dict)


class TestingCache:
    """Serializes test results summaries to JSON caches files."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = os.path.abspath(cache_file_path)
        self.data = TestCacheData()
        self.load()

    def _get_key(self, prompt: str, context_hash: str) -> str:
        raw = f"{prompt}:{context_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def load(self) -> None:
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.data = TestCacheData.model_validate(raw)
            except Exception:
                self.data = TestCacheData()

    def get(self, prompt: str, context_hash: str) -> Optional[Dict[str, Any]]:
        key = self._get_key(prompt, context_hash)
        entry = self.data.entries.get(key)
        if entry:
            return entry.result_data
        return None

    def set(self, prompt: str, context_hash: str, results: Dict[str, Any]) -> None:
        key = self._get_key(prompt, context_hash)
        self.data.entries[key] = TestCachePayload(
            prompt=prompt,
            context_hash=context_hash,
            result_data=results,
            timestamp=time.time(),
        )

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self.data.model_dump(), f, indent=2)
        except Exception:
            pass


from typing import Any
