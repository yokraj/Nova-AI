"""Vision Memory integration packages observations into long-term RAG.
"""

import structlog
from typing import Optional, Any
from uuid import UUID
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.memory.models import MemoryType

logger = structlog.get_logger("vision_memory")

class VisionMemory:
    """Stores visual summaries, layouts, and OCR text in system memory."""

    def __init__(self, memory_engine: Optional[Any] = None) -> None:
        try:
            self.memory = memory_engine or LocalMemoryEngine()
        except Exception:
            self.memory = None

    async def store_observation(self, summary: str, ocr_text: str, layout_desc: str) -> Optional[UUID]:
        """Indexes visual context block descriptions into the long-term memory."""
        if not self.memory:
            return None
            
        try:
            content = (
                f"Visual Observation: {summary}\n"
                f"Screen Text Context: {ocr_text}\n"
                f"Layout Structure: {layout_desc}"
            )
            return await self.memory.store_memory(
                content=content,
                memory_type=MemoryType.SYSTEM,
                metadata={"source": "vision_engine"}
            )
        except Exception as e:
            logger.warning("Failed to store visual observation in long-term memory", error=str(e))
            return None
