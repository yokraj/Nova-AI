"""Plugin Memory — bridges plugin metadata and execution events with RAG vector store."""

from typing import Any, Dict, Optional
import structlog

from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway
from app.ai.memory import LocalMemoryEngine, MemoryType

logger = structlog.get_logger("plugin_memory")


class PluginMemory:
    """Persists plugin capabilities and execution logs in RAG vector memory store.

    Follows the identical bridge pattern used by LearningMemory, MissionMemory, and SafetyMemory.
    """

    def __init__(self, memory_engine: Optional[LocalMemoryEngine] = None) -> None:
        self._memory = memory_engine

    @property
    def memory(self) -> Any:
        """Resolve memory engine lazily via DI container."""
        if self._memory is None:
            try:
                gateway = resolve(IAIGateway)
                self._memory = gateway.memory
            except Exception:
                pass
        return self._memory

    async def persist_plugin_info(
        self,
        plugin_id: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Index plugin specification in RAG database."""
        engine = self.memory
        if not engine:
            return

        meta = metadata or {}
        meta["plugin_id"] = plugin_id
        meta["category"] = "plugin_info"

        try:
            await engine.store_memory(
                content=description,
                memory_type=MemoryType.CONVERSATION,
                metadata=meta,
            )
            logger.info("Persisted plugin info in RAG store", plugin_id=plugin_id)
        except Exception as err:
            logger.error("Failed to index plugin info", error=str(err))
