"""Shared Blackboard accessible by all swarm agents for scratchpad data and intermediate results."""

from typing import Any, Dict, Optional
import structlog

from app.ai.swarm.interfaces import ISharedBlackboard
from app.ai.swarm.models import BlackboardEntry

logger = structlog.get_logger("shared_blackboard")


class SharedBlackboard(ISharedBlackboard):
    """Shared scratchpad and state board accessible by all swarm agents."""

    def __init__(self) -> None:
        self._entries: Dict[str, BlackboardEntry] = {}

    async def write(self, key: str, value: Any, author_agent_id: str) -> BlackboardEntry:
        """Write entry to blackboard."""
        entry = BlackboardEntry(key=key, value=value, author_agent_id=author_agent_id)
        self._entries[key] = entry
        logger.info("Blackboard entry written", key=key, author=author_agent_id)
        return entry

    async def read(self, key: str) -> Optional[Any]:
        """Read entry from blackboard."""
        entry = self._entries.get(key)
        return entry.value if entry else None
