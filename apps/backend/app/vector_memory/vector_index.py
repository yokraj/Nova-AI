"""Vector Index Manager Module.

Manages domain vector space indexes across Memory entries, Conversations, Projects,
Workspaces, User preferences, Documents, Codebases, and Git repositories.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.embedding_engine import EmbeddingEngine
from app.vector_memory.vector_store import VectorStore

logger = structlog.get_logger(__name__)


class VectorIndexManager:
    """Enterprise Domain Vector Indexing Manager."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        vector_store: Optional[VectorStore] = None,
    ) -> None:
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = vector_store or VectorStore()
        logger.info("vector_index_manager_initialized")

    async def index_memory(
        self,
        memory_id: str,
        text: str,
        index_domain: str = "memory",
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Indexes a memory, conversation, project, or document item into vector space."""
        embed_res = await self.embedding_engine.generate_embedding(text, context_type=index_domain)
        vector = embed_res["vector"]

        metadata = {
            "memory_id": memory_id,
            "index_domain": index_domain,
            "workspace": workspace,
            "project": project,
            "model_name": embed_res["model_name"],
            "dimension": embed_res["dimension"],
            "text_snippet": text[:150],
        }

        await self.vector_store.add_vector(memory_id, vector, metadata)
        logger.info("vector_indexed", memory_id=memory_id, index_domain=index_domain, workspace=workspace)

        return {
            "memory_id": memory_id,
            "index_domain": index_domain,
            "vector_dimension": embed_res["dimension"],
            "model_name": embed_res["model_name"],
        }
