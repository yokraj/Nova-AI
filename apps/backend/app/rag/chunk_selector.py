"""Chunk Selector Module.

Selects granular text chunks within strict token budget constraints to prevent context window overflow.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig

logger = structlog.get_logger(__name__)


class ChunkSelector:
    """Enterprise Granular Text Chunk Selection & Token Budgeting Engine."""

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = config or RAGConfig()
        logger.info("chunk_selector_initialized")

    def select_chunks(
        self, documents: List[Dict[str, Any]], max_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Selects and truncates text chunks fitting strictly within max token budget."""
        token_budget = max_tokens or self.config.max_context_tokens
        selected_chunks: List[Dict[str, Any]] = []
        accumulated_tokens = 0

        for doc in documents:
            content = doc.get("content") or doc.get("summary") or ""
            words = content.split()
            estimated_tokens = int(len(words) * 1.3)

            if accumulated_tokens + estimated_tokens > token_budget:
                # Truncate content to fit remaining budget
                remaining_tokens = token_budget - accumulated_tokens
                allowed_words = int(remaining_tokens / 1.3)
                if allowed_words > 10:
                    truncated_text = " ".join(words[:allowed_words]) + "..."
                    doc_copy = dict(doc)
                    doc_copy["content"] = truncated_text
                    selected_chunks.append(doc_copy)
                    accumulated_tokens += remaining_tokens
                break
            else:
                selected_chunks.append(doc)
                accumulated_tokens += estimated_tokens

        logger.info("chunks_selected", chunk_count=len(selected_chunks), total_tokens=accumulated_tokens)
        return selected_chunks
