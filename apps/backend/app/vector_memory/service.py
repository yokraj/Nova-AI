"""Vector Service Layer Module.

Provides decoupled asynchronous business service abstractions:
EmbeddingService, VectorSearchService, VectorIndexService, and StatisticsService.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.vector_memory.repository import VectorRepository
from app.vector_memory.embedding_engine import EmbeddingEngine
from app.vector_memory.vector_store import VectorStore
from app.vector_memory.vector_index import VectorIndexManager
from app.vector_memory.vector_search import VectorSearch
from app.vector_memory.statistics import VectorStatisticsTracker
from app.vector_memory.health import VectorHealthChecker
from app.vector_memory.schemas import (
    EmbeddingCreateRequest,
    BatchEmbeddingRequest,
    EmbeddingResponse,
    VectorSearchResult,
    VectorHealthResponse,
    VectorStatisticsResponse,
)

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Business service handling single and batch embedding generation, deletion, and reindexing."""

    def __init__(self, repository: VectorRepository) -> None:
        self.repository = repository
        self.engine = EmbeddingEngine()
        self.vector_store = VectorStore()
        logger.info("embedding_service_initialized")

    async def create_embedding(self, request: EmbeddingCreateRequest) -> EmbeddingResponse:
        """Generates and persists embedding vector for text."""
        res = await self.engine.generate_embedding(request.text, model_name=request.model_name)
        mem_id = request.memory_id or "mem-standalone"

        record = await self.repository.save_embedding(
            memory_id=mem_id,
            vector=res["vector"],
            model_name=res["model_name"],
            workspace=request.workspace,
            project=request.project,
        )

        await self.vector_store.add_vector(
            mem_id,
            res["vector"],
            {
                "workspace": request.workspace,
                "project": request.project,
                "model_name": res["model_name"],
                "dimension": res["dimension"],
                "is_neural": res.get("is_neural", True),
                "text_snippet": request.text[:150],
            },
        )

        return EmbeddingResponse(
            id=record.id,
            memory_id=record.memory_id,
            model_name=record.model_name,
            dimension=record.dimension,
            vector=res["vector"],
            workspace=record.workspace,
            project=record.project,
            created_at=record.created_at,
        )

    async def create_batch(self, request: BatchEmbeddingRequest) -> List[EmbeddingResponse]:
        """Generates and persists batch embedding vectors."""
        responses = []
        for idx, text in enumerate(request.texts):
            mem_id = request.memory_ids[idx] if request.memory_ids and idx < len(request.memory_ids) else f"mem-batch-{idx}"
            single_req = EmbeddingCreateRequest(
                text=text,
                memory_id=mem_id,
                model_name=request.model_name,
                workspace=request.workspace,
                project=request.project,
            )
            emb = await self.create_embedding(single_req)
            responses.append(emb)
        return responses

    async def get_embedding(self, embedding_id: str) -> Optional[EmbeddingResponse]:
        """Fetches embedding record by ID."""
        record = await self.repository.get_embedding(embedding_id)
        if not record:
            return None
        return EmbeddingResponse(
            id=record.id,
            memory_id=record.memory_id,
            model_name=record.model_name,
            dimension=record.dimension,
            vector=record.vector_json if isinstance(record.vector_json, list) else [],
            workspace=record.workspace,
            project=record.project,
            created_at=record.created_at,
        )

    async def delete_embedding(self, embedding_id: str) -> bool:
        """Deletes embedding record by ID."""
        return await self.repository.delete_embedding(embedding_id)

    async def reindex_all(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reindexes items into vector store."""
        return await self.engine.reindex(items)


class VectorSearchService:
    """Business service handling semantic vector search and candidate candidate retrieval."""

    def __init__(self, repository: VectorRepository) -> None:
        self.repository = repository
        self.search_engine = VectorSearch()
        logger.info("vector_search_service_initialized")

    async def search(
        self,
        query: str,
        top_k: int = 10,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Performs semantic vector search."""
        return await self.search_engine.semantic_search(
            query, top_k=top_k, workspace=workspace, project=project, threshold=threshold
        )


class VectorIndexService:
    """Business service handling domain vector indexing."""

    def __init__(self, repository: VectorRepository) -> None:
        self.repository = repository
        self.index_manager = VectorIndexManager()
        logger.info("vector_index_service_initialized")

    async def index_item(
        self,
        memory_id: str,
        text: str,
        index_domain: str = "memory",
        workspace: str = "Nova",
        project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Indexes item into domain vector index."""
        return await self.index_manager.index_memory(
            memory_id=memory_id, text=text, index_domain=index_domain, workspace=workspace, project=project
        )


class StatisticsService:
    """Business service handling vector database telemetry and health diagnostics."""

    def __init__(self, repository: VectorRepository) -> None:
        self.repository = repository
        self.stats_tracker = VectorStatisticsTracker()
        self.health_checker = VectorHealthChecker()
        logger.info("statistics_service_initialized")

    async def get_statistics(self) -> VectorStatisticsResponse:
        """Returns platform vector database telemetry."""
        count = await self.repository.get_embeddings_count()
        self.stats_tracker._embedding_count = count
        return self.stats_tracker.get_statistics()

    async def check_health(self) -> VectorHealthResponse:
        """Runs vector database diagnostic health checks."""
        return self.health_checker.run_health_checks()
