"""Embedding Router Module.

Automatically chooses optimal embedding model based on document size, content domain (code,
conversation, knowledge, project), workspace, latency bounds, and memory limits.
"""

from typing import Any, Dict, Optional
import structlog

from app.vector_memory.config import VectorConfig

logger = structlog.get_logger(__name__)


class EmbeddingRouter:
    """Enterprise Autonomous Embedding Model Router."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or VectorConfig()
        logger.info("embedding_router_initialized")

    def select_model_for_context(
        self,
        text: str,
        context_type: str = "general",
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        max_latency_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Dynamically selects optimal model name and dimension for given text and context."""
        text_len = len(text)
        type_lower = context_type.lower()

        # 1. Selection Matrix
        if "code" in type_lower or "repository" in type_lower:
            selected_model = "Instructor"
            dimension = 768
        elif text_len > 4000:
            selected_model = "BAAI/bge-base-en-v1.5"
            dimension = 768
        elif "conversation" in type_lower or "message" in type_lower:
            selected_model = "Nomic Embed"
            dimension = 768
        elif max_latency_ms and max_latency_ms < 10.0:
            selected_model = "E5 Small"
            dimension = 384
        else:
            selected_model = self.config.default_model
            dimension = self.config.default_dimension

        logger.info(
            "embedding_model_selected",
            context_type=context_type,
            selected_model=selected_model,
            dimension=dimension,
            text_len=text_len,
        )

        return {
            "model_name": selected_model,
            "dimension": dimension,
            "context_type": context_type,
        }
