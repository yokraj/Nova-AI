"""Knowledge Manager managing personal notes, bookmarks, and knowledge snippets."""

from typing import List
import structlog

logger = structlog.get_logger("knowledge_manager")


class KnowledgeManager:
    """Stores personal notes, bookmarks, and reference information."""

    def __init__(self) -> None:
        self._notes: List[str] = [
            "Nova AI Assistant Spec M3.3.13 completed architecture plan.",
        ]

    async def add_note(self, content: str) -> str:
        """Add personal note."""
        self._notes.append(content)
        logger.info("Saved personal note", length=len(content))
        return content

    async def list_notes(self) -> List[str]:
        """List personal notes."""
        return list(self._notes)
