"""Automation Memory logs execution results to RAG index systems.
"""

import structlog
from typing import Optional, Any
from uuid import UUID

from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.models import MemoryType

logger = structlog.get_logger("automation_memory")

class AutomationMemory:
    """Archives command summaries and performance timings safely."""

    def __init__(self, memory_engine: Optional[Any] = None) -> None:
        try:
            self.memory = memory_engine or LocalMemoryEngine()
        except Exception:
            self.memory = None

    async def store_execution(self, command_summary: str, results_summary: str, performance: str) -> Optional[UUID]:
        """Saves execution history content blocks to local database."""
        if not self.memory:
            return None

        try:
            content = (
                f"Automation Command Execution: {command_summary}\n"
                f"Step Logs Output: {results_summary}\n"
                f"Performance Timings: {performance}"
            )
            return await self.memory.store_memory(
                content=content,
                memory_type=MemoryType.SYSTEM,
                metadata={"source": "automation_engine"}
            )
        except Exception as err:
            logger.warning("Failed to write execution log to memory RAG database", error=str(err))
            return None
