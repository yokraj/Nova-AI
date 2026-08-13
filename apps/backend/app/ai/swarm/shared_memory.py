"""Shared Memory store for inter-agent data exchange."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("shared_memory")


class SharedMemory:
    """Inter-agent shared memory store."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    async def store(self, key: str, value: Any) -> None:
        """Store value in shared memory."""
        self._store[key] = value

    async def retrieve(self, key: str) -> Any:
        """Retrieve value from shared memory."""
        return self._store.get(key)
