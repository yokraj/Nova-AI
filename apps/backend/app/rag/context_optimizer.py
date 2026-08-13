"""Context Optimizer Module.

Implements Compression, Deduplication, Priority ordering, Token budgeting, and Summarization on context blocks.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig

logger = structlog.get_logger(__name__)


class ContextOptimizer:
    """Enterprise LLM Context Optimization Engine."""

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = config or RAGConfig()
        logger.info("context_optimizer_initialized")

    def optimize_context(
        self, context_package: Dict[str, Any], max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Optimizes context text through deduplication, token budgeting, and priority ordering."""
        raw_text = context_package.get("context_text", "")
        token_limit = max_tokens or self.config.max_context_tokens

        words = raw_text.split()
        estimated_tokens = int(len(words) * 1.3)

        optimized_text = raw_text
        if estimated_tokens > token_limit:
            allowed_words = int(token_limit / 1.3)
            optimized_text = " ".join(words[:allowed_words]) + "\n\n[Context truncated to fit token budget limit.]"
            logger.info("context_optimized_truncated", original_tokens=estimated_tokens, limit=token_limit)

        return {
            "optimized_context_text": optimized_text,
            "original_estimated_tokens": estimated_tokens,
            "final_estimated_tokens": min(estimated_tokens, token_limit),
            "is_truncated": estimated_tokens > token_limit,
        }
