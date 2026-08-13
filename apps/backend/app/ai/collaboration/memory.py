"""Memory integration persisting collaboration logs and decisions to RAG vector stores.
"""

import structlog
from typing import Any, Optional, Dict
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("collaboration_memory")

class CollaborationMemory:
    """Interfaces collaboration threads with the Local Memory Engine for vector lookups."""

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

    async def persist_collaboration(self, correlation_id: str, summary_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes collaboration trace logs and consensus outcomes into the memory engine."""
        engine = self.memory
        if not engine:
            logger.debug("Memory engine unavailable. Skipping history indexing.")
            return

        meta = metadata or {}
        meta["correlation_id"] = correlation_id
        meta["category"] = "collaboration_session"

        try:
            await engine.store_memory(
                content=summary_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta
            )
            logger.info("Persisted collaboration transcript in RAG database", correlation_id=correlation_id)
        except Exception as err:
            logger.error("Failed to index collaboration transcript in PGVector/FAISS store", error=str(err))
