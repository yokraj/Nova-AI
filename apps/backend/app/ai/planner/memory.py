"""Memory integration layer storing execution plans summaries.
"""

import structlog
from typing import Optional, Any
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.models import MemoryType

logger = structlog.get_logger("planner_memory")

class PlannerMemory:
    """Archives session inputs and generated scheduling plans into database RAG memory."""

    def __init__(self, memory_engine: Optional[Any] = None) -> None:
        try:
            self.memory = memory_engine or LocalMemoryEngine()
        except Exception:
            self.memory = None

    async def store_plan(self, session_id: str, goal_desc: str, plan_summary: str) -> None:
        """Stores plan summary string structures in local database vector store."""
        if not self.memory:
            return

        try:
            content = (
                f"Planner Session: {session_id}\n"
                f"Goal Description: {goal_desc}\n"
                f"Plan Summary: {plan_summary}"
            )
            await self.memory.store_memory(
                content=content,
                memory_type=MemoryType.SYSTEM,
                metadata={"source": "planner_engine", "session_id": session_id}
            )
        except Exception as err:
            logger.warning("Failed to archive compiled planning plan in memory database", error=str(err))
