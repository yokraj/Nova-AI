"""Memory integration indexing completed missions logs to the RAG database.
"""

import structlog
from typing import Any, Optional, Dict
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("mission_memory")

class MissionMemory:
    """Bridges active mission execution logs with vector memory stores."""

    def __init__(self, memory_engine: Optional[LocalMemoryEngine] = None) -> None:
        self._memory = memory_engine

    @property
    def memory(self) -> Any:
        if self._memory is None:
            try:
                gateway = resolve(IAIGateway)
                self._memory = gateway.memory
            except Exception:
                pass
        return self._memory

    async def persist_mission(self, mission_id: str, summary_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes mission execution summary inside vector memory database."""
        engine = self.memory
        if not engine:
            logger.debug("Memory engine unavailable. Skipping history indexing.")
            return

        meta = metadata or {}
        meta["mission_id"] = mission_id
        meta["category"] = "mission_session"

        try:
            await engine.store_memory(
                content=summary_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta
            )
            logger.info("Persisted mission history summary in RAG database", mission_id=mission_id)
        except Exception as err:
            logger.error("Failed to index mission summary in vector store", error=str(err))
