"""Retrieval Engine coordinates searches, similarity thresholds, and ranking pipelines.
"""

from typing import List
from app.ai.memory.vector_store import IVectorStore
from app.ai.memory.embedding_manager import EmbeddingManager
from app.ai.memory.ranking_engine import RankingEngine
from app.ai.memory.context_builder import ContextBuilder
from app.ai.memory.models import ContextPackage

class RetrievalEngine:
    """Orchestrates query embeddings conversions, vector database scans, and context formatters."""

    def __init__(self, store: IVectorStore, embedding_mgr: EmbeddingManager) -> None:
        self.store = store
        self.embedding_mgr = embedding_mgr
        self.ranker = RankingEngine()
        self.builder = ContextBuilder()

    async def retrieve_context(self, query: str, limit: int = 5, threshold: float = 0.7) -> ContextPackage:
        """Runs full RAG context lookup flow: Embed -> Vector Scan -> Rank -> Build Context."""
        query_vector = await self.embedding_mgr.embed_text(query)
        results = await self.store.search(query_vector, limit=limit, threshold=threshold)
        
        # Rank by score computations (Similarity, Recency, Importance)
        ranked = self.ranker.rank_results(results)
        
        # Build ContextPackage output
        return self.builder.build_context_package(ranked)
