"""Nova AI Enterprise Vector Database & Embedding Engine Package.

Exports vector models, repositories, embedding engine, router, vector store, similarity metrics,
ranking, optimizer, cache, health checker, statistics tracker, services, and VectorEngine master orchestrator.
"""

from app.vector_memory.config import VectorConfig
from app.vector_memory.exceptions import (
    VectorError,
    EmbeddingGenerationError,
    VectorDimensionMismatchError,
    VectorStoreError,
    VectorIndexNotFoundError,
    VectorCacheError,
    VectorHealthError,
)
from app.vector_memory.models import (
    EmbeddingModel,
    EmbeddingModelRegistry,
    EmbeddingJobModel,
    VectorIndexModel,
    VectorStatisticsModel,
)
from app.vector_memory.schemas import (
    EmbeddingCreateRequest,
    BatchEmbeddingRequest,
    EmbeddingResponse,
    VectorSearchRequest,
    VectorSearchResult,
    VectorHealthResponse,
    VectorStatisticsResponse,
)
from app.vector_memory.embedding_models import ModelRegistry, BaseEmbeddingProvider
from app.vector_memory.embedding_router import EmbeddingRouter
from app.vector_memory.embedding_engine import EmbeddingEngine
from app.vector_memory.vector_store import VectorStore, SQLiteVectorStoreBackend
from app.vector_memory.similarity import SimilarityEngine
from app.vector_memory.ranking import VectorRankingEngine
from app.vector_memory.vector_cache import VectorCache
from app.vector_memory.vector_optimizer import VectorOptimizer
from app.vector_memory.vector_index import VectorIndexManager
from app.vector_memory.vector_search import VectorSearch
from app.vector_memory.statistics import VectorStatisticsTracker
from app.vector_memory.health import VectorHealthChecker
from app.vector_memory.repository import VectorRepository
from app.vector_memory.service import (
    EmbeddingService,
    VectorSearchService,
    VectorIndexService,
    StatisticsService,
)
from app.vector_memory.engine import VectorEngine

__all__ = [
    "VectorConfig",
    "VectorError",
    "EmbeddingGenerationError",
    "VectorDimensionMismatchError",
    "VectorStoreError",
    "VectorIndexNotFoundError",
    "VectorCacheError",
    "VectorHealthError",
    "EmbeddingModel",
    "EmbeddingModelRegistry",
    "EmbeddingJobModel",
    "VectorIndexModel",
    "VectorStatisticsModel",
    "EmbeddingCreateRequest",
    "BatchEmbeddingRequest",
    "EmbeddingResponse",
    "VectorSearchRequest",
    "VectorSearchResult",
    "VectorHealthResponse",
    "VectorStatisticsResponse",
    "ModelRegistry",
    "BaseEmbeddingProvider",
    "EmbeddingRouter",
    "EmbeddingEngine",
    "VectorStore",
    "SQLiteVectorStoreBackend",
    "SimilarityEngine",
    "VectorRankingEngine",
    "VectorCache",
    "VectorOptimizer",
    "VectorIndexManager",
    "VectorSearch",
    "VectorStatisticsTracker",
    "VectorHealthChecker",
    "VectorRepository",
    "EmbeddingService",
    "VectorSearchService",
    "VectorIndexService",
    "StatisticsService",
    "VectorEngine",
]
