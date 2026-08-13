"""Memory integration layer storing agent logs and telemetry metadata.
"""

import structlog
from typing import Optional, Any
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.models import MemoryType

logger = structlog.get_logger("agent_memory")

class AgentMemory:
    """Interfaces with LocalMemoryEngine vector store indexes, handling fallbacks."""

    def __init__(self, memory_engine: Optional[Any] = None) -> None:
        try:
            self.memory = memory_engine or LocalMemoryEngine()
        except Exception:
            self.memory = None

    async def store_event(self, agent_id: str, event_type: str, details: str) -> None:
        """Archives lifecycle and execution summaries into local database indexes."""
        if not self.memory:
            return

        try:
            content = f"Agent '{agent_id}' Event: {event_type}. Details: {details}."
            await self.memory.store_memory(
                content=content,
                memory_type=MemoryType.SYSTEM,
                metadata={"source": "agent_foundation", "agent_id": agent_id}
            )
        except Exception as err:
            logger.warning("Failed to index agent metadata inside database vector store", error=str(err))
