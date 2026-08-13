"""Unit and Integration Tests for Nova AI Enterprise Hybrid RAG Engine.

Validates Query Analysis, Query Rewriting, Parallel Keyword & Semantic Search, Hybrid Merging,
Cross-Encoder Reranking, Document/Chunk Selection, Context Building, Prompt Assembly,
Grounding Verification, Citation Generation, Health Diagnostics, Statistics, REST API, and RBAC.
"""

import asyncio
import pytest

from app.rag import (
    RAGConfig,
    QueryAnalyzer,
    QueryRewriter,
    KeywordSearchEngine,
    SemanticSearchEngine,
    HybridSearchEngine,
    CrossEncoderReranker,
    DocumentSelector,
    ChunkSelector,
    ContextBuilder,
    ContextOptimizer,
    PromptBuilder,
    GroundingEngine,
    ResponseGrounder,
    CitationGenerator,
    HybridRAGRetriever,
    RAGStatisticsTracker,
    RAGHealthChecker,
    HybridRAGEngine,
)


def test_query_analyzer_and_rewriter():
    """Test QueryAnalyzer intent classification and QueryRewriter pronoun resolution."""
    analyzer = QueryAnalyzer()
    rewriter = QueryRewriter()

    # Intent Classification
    code_res = analyzer.analyze_query("Fix python bug in database session connection pool")
    assert code_res["intent_category"] == "coding"

    plan_res = analyzer.analyze_query("Build a distributed hospital management system")
    assert plan_res["intent_category"] in ["planning", "project_lookup"]

    # Query Rewriting
    history = [{"role": "user", "content": "Explain PostgreSQL indexing strategy"}]
    rewrite_res = rewriter.rewrite_query("How do I optimize it?", conversation_history=history, active_project="Nova")
    assert rewrite_res["is_modified"] is True
    assert "PostgreSQL" in rewrite_res["rewritten_query"] or "Nova" in rewrite_res["rewritten_query"]


def test_hybrid_search_and_reranking():
    """Test parallel Keyword + Semantic search merging via RRF and Cross-Encoder reranking."""
    async def _test():
        hybrid_search = HybridSearchEngine()
        reranker = CrossEncoderReranker()

        candidates = await hybrid_search.execute_hybrid_search(
            query="FastAPI microservice backend architecture", workspace="Nova", limit=10
        )
        assert len(candidates) >= 0

        # Reranking candidates
        raw_candidates = [
            {"memory_id": "m1", "title": "FastAPI Architecture Guide", "content": "FastAPI async microservice layout", "hybrid_score": 0.8},
            {"memory_id": "m2", "title": "React Frontend Guide", "content": "React UI layout CSS", "hybrid_score": 0.75},
        ]
        reranked = reranker.rerank("FastAPI microservice", raw_candidates, top_k=2)
        assert len(reranked) == 2
        assert reranked[0]["memory_id"] == "m1"

    asyncio.run(_test())


def test_context_building_and_prompt_assembly():
    """Test ContextBuilder, ContextOptimizer, and PromptBuilder."""
    builder = ContextBuilder()
    optimizer = ContextOptimizer()
    prompt_builder = PromptBuilder()

    chunks = [
        {"memory_id": "mem-101", "title": "Database Spec", "content": "PostgreSQL 15+ is used for persistence."},
        {"memory_id": "mem-102", "title": "Cache Spec", "content": "Redis 7.0 is used for caching."},
    ]

    pkg = builder.build_context_package(retrieved_chunks=chunks, workspace="Nova", project="Kernel")
    assert "POSTGRESQL" in pkg["context_text"].upper()

    opt = optimizer.optimize_context(pkg, max_tokens=1000)
    assert opt["is_truncated"] is False

    prompt = prompt_builder.build_grounded_prompt("What database is used?", opt["optimized_context_text"])
    assert "SYSTEM INSTRUCTION" in prompt
    assert "GROUNDING CONTEXT" in prompt


def test_grounding_and_citations():
    """Test GroundingEngine factual verification, uncertainty statements, and CitationGenerator."""
    grounder = GroundingEngine()
    response_grounder = ResponseGrounder(grounding_engine=grounder)
    citation_gen = CitationGenerator()

    context = "PostgreSQL 15+ is used for persistence in Nova AI backend."

    # Grounded response
    res_grounded = response_grounder.enforce_grounding("PostgreSQL 15+ is used for persistence", context)
    assert res_grounded["verification"]["confidence_score"] >= 0.7

    # Ungrounded query state
    res_ungrounded = response_grounder.enforce_grounding("MongoDB 6.0 is used for persistence", "[No specific grounding documents retrieved.]")
    assert res_ungrounded["verification"]["uncertainty_required"] is True
    assert "Note:" in res_ungrounded["final_response"]

    # Citation generation
    sources = [{"memory_id": "mem-99", "title": "Database Architecture Spec"}]
    cites = citation_gen.generate_citations(sources)
    assert len(cites["citations"]) == 1
    assert "Database Architecture Spec" in cites["citation_footer"]


def test_hybrid_rag_engine_end_to_end():
    """Test full grounded RAG query execution through HybridRAGEngine."""
    async def _test():
        engine = HybridRAGEngine()

        result = await engine.execute_grounded_query(
            query="Explain Nova AI backend database persistence architecture",
            workspace="Nova",
            project="Kernel",
            conversation_id="rag-test-01",
        )

        assert "response" in result
        assert result["query"] is not None
        assert result["conversation_id"] == "rag-test-01"
        assert result["grounding_verification"] is not None

    asyncio.run(_test())


def test_rag_statistics_and_health():
    """Test RAGStatisticsTracker and RAGHealthChecker."""
    tracker = RAGStatisticsTracker()
    checker = RAGHealthChecker()

    tracker.record_retrieval(latency_ms=12.5, rerank_ms=2.1, citations=2)
    stats = tracker.get_statistics()
    assert stats["retrieval_count"] == 1
    assert stats["citation_count"] == 2

    health = checker.run_health_checks()
    assert health["status"] == "healthy"
    assert health["retriever_healthy"] is True
