"""Vector Search Module.

Implements VectorSearch providing semantic_search, similar_documents, similar_conversations,
similar_projects, similar_workspace, nearest_neighbors, and hybrid_candidates.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.embedding_engine import EmbeddingEngine
from app.vector_memory.vector_store import VectorStore
from app.vector_memory.similarity import SimilarityEngine
from app.vector_memory.ranking import VectorRankingEngine
from app.vector_memory.vector_cache import VectorCache
from app.vector_memory.schemas import VectorSearchResult

logger = structlog.get_logger(__name__)


class VectorSearch:
    """Enterprise Vector Similarity & Semantic Search Engine."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        vector_store: Optional[VectorStore] = None,
        cache: Optional[VectorCache] = None,
        ranking_engine: Optional[VectorRankingEngine] = None,
    ) -> None:
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = vector_store or VectorStore()
        self.cache = cache or VectorCache()
        self.ranking_engine = ranking_engine or VectorRankingEngine()
        logger.info("vector_search_initialized")

    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Performs semantic vector search for a text query string."""
        embed_res = await self.embedding_engine.generate_embedding(query)
        query_vector = embed_res["vector"]

        candidates = await self.vector_store.search_vectors(query_vector, top_k=top_k * 2)
        filtered = SimilarityEngine.filter_by_threshold(candidates, threshold)
        ranked = self.ranking_engine.rank_candidates(filtered, target_workspace=workspace, target_project=project)

        results = []
        for r in ranked[:top_k]:
            meta = r.get("metadata", {})
            results.append(
                VectorSearchResult(
                    memory_id=r["memory_id"],
                    similarity_score=r.get("composite_rank_score", r["similarity_score"]),
                    distance=r["distance"],
                    model_name=meta.get("model_name", embed_res["model_name"]),
                    workspace=meta.get("workspace", workspace or "Nova"),
                    project=meta.get("project", project),
                    text_snippet=meta.get("text_snippet"),
                )
            )

        logger.info("semantic_search_executed", query_snippet=query[:30], count=len(results))
        return results

    async def similar_documents(self, document_text: str, top_k: int = 5) -> List[VectorSearchResult]:
        """Finds documents similar to target document text."""
        return await self.semantic_search(document_text, top_k=top_k)

    async def similar_conversations(self, message_text: str, top_k: int = 5) -> List[VectorSearchResult]:
        """Finds past conversation turns similar to message text."""
        return await self.semantic_search(message_text, top_k=top_k)

    async def similar_projects(self, project_query: str, top_k: int = 5) -> List[VectorSearchResult]:
        """Finds project architectural entries similar to project query."""
        return await self.semantic_search(project_query, top_k=top_k)

    async def similar_workspace(self, workspace_name: str, top_k: int = 5) -> List[VectorSearchResult]:
        """Finds memories similar within workspace scope."""
        return await self.semantic_search(workspace_name, workspace=workspace_name, top_k=top_k)

    async def nearest_neighbors(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieves raw nearest neighbor vector records."""
        return await self.vector_store.search_vectors(query_vector, top_k=top_k)

    async def hybrid_candidates(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Retrieves candidate vectors prepared for hybrid RAG reranking."""
        embed_res = await self.embedding_engine.generate_embedding(query)
        candidates = await self.vector_store.search_vectors(embed_res["vector"], top_k=top_k)
        return candidates
