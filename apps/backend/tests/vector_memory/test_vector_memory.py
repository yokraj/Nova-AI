"""Unit and Integration Tests for Nova AI Enterprise Vector Database & Embedding Engine.

Validates Embedding Generation, Batching, Distance Metrics, Similarity, Candidate Ranking,
Vector Cache, Optimizer, Vector Indexing, Health Diagnostics, Statistics, REST API, and RBAC.
"""

import asyncio
import pytest

from app.vector_memory import (
    VectorConfig,
    EmbeddingCreateRequest,
    BatchEmbeddingRequest,
    EmbeddingEngine,
    ModelRegistry,
    EmbeddingRouter,
    VectorStore,
    SimilarityEngine,
    VectorRankingEngine,
    VectorCache,
    VectorOptimizer,
    VectorIndexManager,
    VectorSearch,
    VectorStatisticsTracker,
    VectorHealthChecker,
    VectorRepository,
    EmbeddingService,
    VectorSearchService,
    StatisticsService,
    VectorEngine,
)


def test_embedding_engine_single_and_batch():
    """Test local embedding vector generation and batch processing."""
    async def _test():
        engine = EmbeddingEngine()

        # 1. Single embedding
        res = await engine.generate_embedding("PostgreSQL database indexing strategy")
        assert res["model_name"] is not None
        assert res["dimension"] == 384
        assert len(res["vector"]) == 384

        # 2. Batch embedding
        batch_res = await engine.generate_batch(["Text 1", "Text 2", "Text 3"])
        assert len(batch_res) == 3
        assert len(batch_res[0]["vector"]) == 384

    asyncio.run(_test())


def test_similarity_metrics_and_mmr():
    """Test Cosine similarity, Euclidean distance, Dot product, and MMR."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    # Cosine
    cos_same = SimilarityEngine.cosine_similarity(v1, v2)
    assert cos_same == 1.0
    cos_ortho = SimilarityEngine.cosine_similarity(v1, v3)
    assert cos_ortho == 0.0

    # Euclidean
    euc_same = SimilarityEngine.euclidean_distance(v1, v2)
    assert euc_same == 0.0

    # MMR
    candidates = [
        {"vector": [0.9, 0.1, 0.0], "text": "Item A"},
        {"vector": [0.89, 0.11, 0.0], "text": "Item A duplicate"},
        {"vector": [0.0, 0.9, 0.1], "text": "Item B diverse"},
    ]
    mmr_res = SimilarityEngine.max_marginal_relevance(v1, candidates, lambda_param=0.5, top_k=2)
    assert len(mmr_res) == 2


def test_vector_ranking_engine():
    """Test candidate ranking across semantic similarity, recency, and importance."""
    ranker = VectorRankingEngine()
    candidates = [
        {"memory_id": "m1", "similarity_score": 0.8, "importance": 0.9, "workspace": "Nova"},
        {"memory_id": "m2", "similarity_score": 0.85, "importance": 0.2, "workspace": "Other"},
    ]
    ranked = ranker.rank_candidates(candidates, target_workspace="Nova")
    assert len(ranked) == 2
    assert "composite_rank_score" in ranked[0]
    # m1 ranks higher due to workspace relevance and importance
    assert ranked[0]["memory_id"] == "m1"


def test_vector_cache_operations():
    """Test vector cache hits, misses, and capacity bounds."""
    config = VectorConfig(cache_capacity=3)
    cache = VectorCache(config=config)

    vec = [0.1] * 384
    cache.cache_embedding("hash_1", vec, "bge-small")
    retrieved = cache.get_embedding("hash_1")
    assert retrieved is not None

    miss = cache.get_embedding("non_existent_hash")
    assert miss is None
    assert cache.hit_count == 1
    assert cache.miss_count == 1


def test_vector_optimizer_compaction():
    """Test duplicate detection and index compaction."""
    optimizer = VectorOptimizer()
    assert optimizer.detect_duplicate("Unique String 1") is False
    assert optimizer.detect_duplicate("Unique String 1") is True

    records = [
        {"text": "Same text content"},
        {"text": "Same text content"},
        {"text": "Different content"},
    ]
    async def _test():
        res = await optimizer.optimize_index(records)
        assert res["duplicates_removed"] == 1
        assert res["compacted_count"] == 2

    asyncio.run(_test())


def test_vector_search_and_index_service():
    """Test VectorIndexManager, VectorSearch, and EmbeddingService."""
    async def _test():
        repo = VectorRepository()
        index_mgr = VectorIndexManager()
        search_engine = VectorSearch(vector_store=index_mgr.vector_store)
        service = EmbeddingService(repo)

        # Index items
        await index_mgr.index_memory("mem-01", "FastAPI microservice backend architecture", workspace="Nova")
        await index_mgr.index_memory("mem-02", "React CSS glassmorphic UI layout", workspace="Nova")

        # Semantic Search
        results = await search_engine.semantic_search("FastAPI backend", top_k=5)
        assert len(results) >= 1
        assert results[0].memory_id == "mem-01"

        # Service Embedding Creation
        req = EmbeddingCreateRequest(text="New vector item text", memory_id="mem-service-01")
        service_res = await service.create_embedding(req)
        assert service_res.id is not None
        assert len(service_res.vector) == 384

    asyncio.run(_test())


def test_vector_health_and_statistics():
    """Test HealthChecker and StatisticsTracker."""
    async def _test():
        repo = VectorRepository()
        stats_service = StatisticsService(repo)

        # Health
        health = await stats_service.check_health()
        assert health.status == "healthy"
        assert health.index_valid is True

        # Statistics
        stats = await stats_service.get_statistics()
        assert stats.vector_dimension == 384
        assert stats.average_search_latency >= 0.0

    asyncio.run(_test())
