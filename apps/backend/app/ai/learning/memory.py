"""Learning Memory — bridges experience records with the RAG vector memory store."""

import structlog
from typing import Any, Dict, Optional

from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("learning_memory")


class LearningMemory:
    """Persists experience summaries and strategies into the RAG vector database.

    Follows the identical bridge pattern used by MissionMemory and SafetyMemory,
    lazy-resolving the gateway when the memory engine is not directly injected.
    """

    def __init__(self, memory_engine: Optional[LocalMemoryEngine] = None) -> None:
        self._memory = memory_engine

    @property
    def memory(self) -> Any:
        """Resolve memory engine lazily via the DI container if not injected."""
        if self._memory is None:
            try:
                gateway = resolve(IAIGateway)
                self._memory = gateway.memory
            except Exception:
                pass
        return self._memory

    async def persist_experience(
        self,
        experience_id: str,
        summary_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Index an experience summary inside the vector memory database."""
        engine = self.memory
        if not engine:
            logger.debug(
                "Memory engine unavailable. Skipping experience indexing.",
                experience_id=experience_id,
            )
            return

        meta = metadata or {}
        meta["experience_id"] = experience_id
        meta["category"] = "learning_experience"

        try:
            await engine.store_memory(
                content=summary_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta,
            )
            logger.info(
                "Persisted experience summary in RAG database",
                experience_id=experience_id,
            )
        except Exception as err:
            logger.error(
                "Failed to index experience in vector store",
                error=str(err),
            )

    async def persist_strategy(
        self,
        strategy_id: str,
        strategy_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Index a strategy description inside the vector memory database."""
        engine = self.memory
        if not engine:
            logger.debug(
                "Memory engine unavailable. Skipping strategy indexing.",
                strategy_id=strategy_id,
            )
            return

        meta = metadata or {}
        meta["strategy_id"] = strategy_id
        meta["category"] = "learning_strategy"

        try:
            await engine.store_memory(
                content=strategy_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta,
            )
            logger.info(
                "Persisted strategy in RAG database",
                strategy_id=strategy_id,
            )
        except Exception as err:
            logger.error(
                "Failed to index strategy in vector store",
                error=str(err),
            )
