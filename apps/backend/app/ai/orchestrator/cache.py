"""In-memory multi-modal response cache with TTL and hash lookup for Universal AI Orchestrator.
"""

import hashlib
import time
from typing import Any, Dict, Optional


class OrchestratorCache:
    """Multi-modal response cache storing LLM, reasoning, code, and vision results."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def _hash_key(self, prompt: str, category: str, model_id: str) -> str:
        raw = f"{category}:{model_id}:{prompt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, prompt: str, category: str, model_id: str) -> Optional[Any]:
        key = self._hash_key(prompt, category, model_id)
        entry = self._store.get(key)
        if entry:
            if time.time() - entry["timestamp"] <= self.ttl_seconds:
                return entry["data"]
            else:
                del self._store[key]
        return None

    def set(self, prompt: str, category: str, model_id: str, data: Any) -> None:
        key = self._hash_key(prompt, category, model_id)
        self._store[key] = {
            "data": data,
            "timestamp": time.time(),
        }

    def clear(self) -> None:
        self._store.clear()
