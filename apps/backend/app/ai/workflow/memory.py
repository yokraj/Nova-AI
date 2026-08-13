"""Memory integration indexing completed workflows to the RAG database.
"""

import structlog
from typing import Any, Optional, Dict
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("workflow_memory")

class WorkflowMemory:
    """Bridges workflow logs with the Local RAG Memory Engine."""

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

    async def persist_workflow(self, workflow_id: str, summary_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Indexes completed workflows summary reports inside vector memory database."""
        engine = self.memory
        if not engine:
            logger.debug("Memory engine unavailable. Skipping history indexing.")
            return

        meta = metadata or {}
        meta["workflow_id"] = workflow_id
        meta["category"] = "workflow_session"

        try:
            await engine.store_memory(
                content=summary_text,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta
            )
            logger.info("Persisted workflow history summary in RAG database", workflow_id=workflow_id)
        except Exception as err:
            logger.error("Failed to index workflow summary in vector store", error=str(err))
