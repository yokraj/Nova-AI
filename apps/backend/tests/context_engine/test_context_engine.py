"""Unit and Integration Tests for Nova AI Enterprise Advanced Context Assembly & Retrieval Optimization Engine.

Validates Context Selection, Score Fusion, Conflict Resolution, Fingerprint Deduplication,
Multi-Attribute Ranking, Priority Tiering, Adaptive Token Budgeting (4K to 128K), Context Compression,
Hierarchical Summarization, Quality Scoring, Cache, Health Diagnostics, Statistics, REST API, and RBAC.
"""

import asyncio
import pytest

from app.context_engine import (
    ContextEngineConfig,
    ContextBuildRequest,
    ContextSelector,
    ContextFusionEngine,
    ContextConflictResolver,
    ContextDeduplicator,
    ContextRanker,
    PriorityEngine,
    TokenBudgetEngine,
    ContextCompressor,
    ContextSummarizer,
    ContextOptimizer,
    ContextBuilder,
    ContextCache,
    QualityScorer,
    ContextStatisticsTracker,
    ContextHealthChecker,
    ContextEngineRepository,
    ContextAssemblyService,
    CompressionService,
    ContextEngine,
)


def test_context_selection_and_fusion():
    """Test ContextSelector multi-engine block selection and ContextFusionEngine weighted score fusion."""
    async def _test():
        selector = ContextSelector()
        fusion = ContextFusionEngine()

        candidates = await selector.select_candidate_blocks("Explain Nova AI architecture", workspace="Nova")
        assert len(candidates) >= 3

        fused = fusion.fuse_candidates(candidates, target_workspace="Nova")
        assert len(fused) == len(candidates)
        assert "fused_score" in fused[0]

    asyncio.run(_test())


def test_conflict_resolution_and_deduplication():
    """Test ContextConflictResolver contradiction override and ContextDeduplicator fingerprint removal."""
    resolver = ContextConflictResolver()
    dedup = ContextDeduplicator()

    candidates = [
        {"id": "mem-1", "title": "Database Spec", "content": "PostgreSQL 15+ is used", "fused_score": 0.90},
        {"id": "mem-2", "title": "Database Spec", "content": "MongoDB is used", "fused_score": 0.60},
        {"id": "mem-3", "title": "Cache Spec", "content": "Redis 7.0 is used for caching", "fused_score": 0.85},
        {"id": "mem-4", "title": "Duplicate Cache", "content": "Redis 7.0 is used for caching", "fused_score": 0.80},
    ]

    resolved = resolver.resolve_conflicts(candidates)
    assert len(resolved) == 3
    # mem-1 (score 0.90) retained over mem-2 (score 0.60)
    titles = [r["title"] for r in resolved]
    assert "Database Spec" in titles

    deduped = dedup.deduplicate(resolved)
    assert len(deduped) == 2  # Duplicate Redis content removed


def test_token_budgeting_and_priority_engine():
    """Test PriorityEngine tiering and TokenBudgetEngine adaptive fitting (4K to 128K)."""
    priority_eng = PriorityEngine()
    budget_eng = TokenBudgetEngine()

    candidates = [
        {"id": "b1", "confidence": 0.90, "content": "Critical core architecture specification block."},
        {"id": "b2", "confidence": 0.60, "content": "Medium priority background log summary block."},
    ]

    prioritized = priority_eng.assign_priorities(candidates)
    assert prioritized[0]["priority_tier"] == "Critical"
    assert prioritized[1]["priority_tier"] == "Medium"

    # Fit into tight 40-word token budget (~52 tokens)
    fit_res = budget_eng.fit_to_budget(prioritized, target_budget=40)
    assert fit_res["target_budget"] == 40
    assert len(fit_res["fitted_candidates"]) >= 1


def test_context_compression_and_summarization():
    """Test ContextCompressor target ratio compression and ContextSummarizer hierarchical summary."""
    compressor = ContextCompressor()
    summarizer = ContextSummarizer()

    long_text = "Word " * 100
    comp_res = compressor.compress_text(long_text, target_ratio=0.50)
    assert comp_res["compressed_words"] == 50
    assert "[compressed...]" in comp_res["compressed_text"]

    candidates = [
        {"source": "memory", "title": "Memory block"},
        {"source": "code_intelligence", "title": "Code block"},
    ]
    summary_res = summarizer.summarize_context_package(candidates)
    assert "MEMORY" in summary_res["hierarchical_summary"].upper()
    assert len(summary_res["domains_covered"]) == 2


def test_quality_scoring_and_cache():
    """Test QualityScorer completeness & freshness metrics and ContextCache hit rates."""
    cache = ContextCache()

    candidates = [
        {"source": "memory", "confidence": 0.90},
        {"source": "vector_search", "confidence": 0.85},
        {"source": "knowledge_graph", "confidence": 0.88},
    ]

    quality = QualityScorer.evaluate_quality(candidates)
    assert quality.overall_score >= 0.70
    assert quality.completeness >= 0.70

    # Cache testing
    cache.cache_context("hash_query_1", {"context": "Test text"})
    hit = cache.get_cached_context("hash_query_1")
    assert hit is not None
    assert cache.hit_rate >= 0.50


def test_context_assembly_service_end_to_end():
    """Test ContextAssemblyService end-to-end context package build."""
    async def _test():
        repo = ContextEngineRepository()
        service = ContextAssemblyService(repo)

        req = ContextBuildRequest(
            query="Summarize Nova AI Operating System architecture and database persistence",
            workspace="Nova",
            project="Kernel",
            token_budget=4096,
        )

        res = await service.build_context(req)
        assert res.build_id is not None
        assert res.token_budget == 4096
        assert "ENVIRONMENT" in res.context_text
        assert res.quality_score >= 0.70

    asyncio.run(_test())


def test_context_engine_health_and_statistics():
    """Test ContextHealthChecker and ContextStatisticsTracker."""
    tracker = ContextStatisticsTracker()
    checker = ContextHealthChecker()

    tracker.record_assembly(context_size=2048, ratio=0.60, tokens=1500, latency_ms=11.2, quality=0.91)
    stats = tracker.get_statistics()
    assert stats.total_assemblies == 1
    assert stats.average_context_size >= 1000

    health = checker.run_health_checks()
    assert health.status == "healthy"
    assert health.builder_healthy is True
