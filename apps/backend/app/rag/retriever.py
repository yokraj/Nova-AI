"""Hybrid RAG Retriever Module.

High-level retriever orchestrating parallel keyword & semantic search, hybrid candidate merging,
cross-encoder reranking, document selection, and token-budgeted chunk selection.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.config import RAGConfig
from app.rag.query_analyzer import QueryAnalyzer
from app.rag.query_rewriter import QueryRewriter
from app.rag.hybrid_search import HybridSearchEngine
from app.rag.reranker import CrossEncoderReranker
from app.rag.document_selector import DocumentSelector
from app.rag.chunk_selector import ChunkSelector

logger = structlog.get_logger(__name__)


class HybridRAGRetriever:
    """Enterprise Master Hybrid RAG Retriever."""

    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        query_analyzer: Optional[QueryAnalyzer] = None,
        query_rewriter: Optional[QueryRewriter] = None,
        hybrid_search: Optional[HybridSearchEngine] = None,
        reranker: Optional[CrossEncoderReranker] = None,
        document_selector: Optional[DocumentSelector] = None,
        chunk_selector: Optional[ChunkSelector] = None,
    ) -> None:
        self.config = config or RAGConfig()
        self.query_analyzer = query_analyzer or QueryAnalyzer()
        self.query_rewriter = query_rewriter or QueryRewriter()
        self.hybrid_search = hybrid_search or HybridSearchEngine(config=self.config)
        self.reranker = reranker or CrossEncoderReranker(config=self.config)
        self.document_selector = document_selector or DocumentSelector()
        self.chunk_selector = chunk_selector or ChunkSelector(config=self.config)
        logger.info("hybrid_rag_retriever_initialized")

    async def retrieve_grounded_context(
        self,
        query: str,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Executes full hybrid RAG retrieval pipeline: analyze -> rewrite -> hybrid search -> rerank -> select chunks."""
        # 1. Intent Analysis & Query Rewrite
        analysis = self.query_analyzer.analyze_query(query)
        rewritten = self.query_rewriter.rewrite_query(query, conversation_history=conversation_history, active_project=project)

        effective_query = rewritten["rewritten_query"]

        # 2. Parallel Keyword & Semantic Hybrid Search
        candidates = await self.hybrid_search.execute_hybrid_search(
            effective_query, workspace=workspace, project=project, limit=self.config.top_candidates_limit
        )

        # 3. Cross-Encoder Reranking
        reranked = self.reranker.rerank(effective_query, candidates, top_k=self.config.rerank_top_k)

        # 4. Document & Chunk Selection within Token Budget
        selected_docs = self.document_selector.select_documents(reranked, max_documents=5)
        selected_chunks = self.chunk_selector.select_chunks(selected_docs, max_tokens=self.config.max_context_tokens)

        logger.info("retrieval_pipeline_completed", candidate_count=len(candidates), chunk_count=len(selected_chunks))
        return {
            "query": query,
            "effective_query": effective_query,
            "intent": analysis,
            "candidates_count": len(candidates),
            "reranked_count": len(reranked),
            "selected_chunks": selected_chunks,
        }
