"""Document Selector Module.

Selects the most relevant documents, memories, conversations, project entries, code snippets, and notes.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class DocumentSelector:
    """Enterprise Multi-Artifact Document Selection Engine."""

    def __init__(self) -> None:
        logger.info("document_selector_initialized")

    def select_documents(
        self, candidates: List[Dict[str, Any]], max_documents: int = 5
    ) -> List[Dict[str, Any]]:
        """Filters and selects top diverse artifact documents from candidate pool."""
        selected: List[Dict[str, Any]] = []
        seen_ids = set()

        for item in candidates:
            mem_id = item.get("memory_id")
            if mem_id and mem_id not in seen_ids:
                seen_ids.add(mem_id)
                selected.append(item)
                if len(selected) >= max_documents:
                    break

        logger.info("documents_selected", count=len(selected))
        return selected
