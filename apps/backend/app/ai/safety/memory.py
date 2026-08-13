"""Memory integration indexing resolved safety evaluations to the RAG database.
"""

import structlog
from typing import Any, Optional, Dict
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("safety_memory")

class SafetyMemory:
    """Bridges safety audit logs with vector memory stores."""

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

    async def persist_audit(self, approval_id: str, summary_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes resolved approval audit inside vector memory database."""
        engine = self.memory
        if not engine:
            logger.debug("Memory engine unavailable. Skipping history indexing.")
            return

        meta = metadata or {}
        meta["approval_id"] = approval_id
        meta["category"] = "safety_audit"

        try:
            await engine.store_memory(
                content=summary_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta
            )
            logger.info("Persisted safety audit report in RAG database", approval_id=approval_id)
        except Exception as err:
            logger.error("Failed to index safety audit in vector store", error=str(err))
