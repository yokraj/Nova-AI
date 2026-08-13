"""Vector REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for Embedding generation, deletion, reindexing,
semantic search, similarity candidates, vector database telemetry, and health diagnostics, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.vector_memory.repository import VectorRepository
from app.vector_memory.service import (
    EmbeddingService,
    VectorSearchService,
    StatisticsService,
)
from app.vector_memory.schemas import (
    EmbeddingCreateRequest,
    EmbeddingResponse,
    VectorSearchResult,
    VectorHealthResponse,
    VectorStatisticsResponse,
)

router = APIRouter(prefix="/api/v1/vectors", tags=["Enterprise Vector Engine"])

# Permission dependencies
require_vector_read = Depends(PermissionChecker("vector:read"))
require_vector_write = Depends(PermissionChecker("vector:write"))
require_vector_admin = Depends(PermissionChecker("vector:admin"))


@router.post("/embeddings", response_model=EmbeddingResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_vector_write])
async def create_embedding(request: EmbeddingCreateRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Generates and stores text embedding."""
    service = EmbeddingService(repository=VectorRepository(db))
    return await service.create_embedding(request)


@router.get("/embeddings/{embedding_id}", response_model=EmbeddingResponse, dependencies=[require_vector_read])
async def get_embedding(embedding_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Fetches embedding record by ID."""
    service = EmbeddingService(repository=VectorRepository(db))
    res = await service.get_embedding(embedding_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Embedding '{embedding_id}' not found.")
    return res


@router.delete("/embeddings/{embedding_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_vector_write])
async def delete_embedding(embedding_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Deletes embedding record by ID."""
    service = EmbeddingService(repository=VectorRepository(db))
    deleted = await service.delete_embedding(embedding_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Embedding '{embedding_id}' not found.")


@router.post("/embeddings/reindex", dependencies=[require_vector_admin])
async def reindex_embeddings(items: List[Dict[str, Any]], db: AsyncSession = Depends(get_db)) -> Any:
    """Reindexes batch items into vector space."""
    service = EmbeddingService(repository=VectorRepository(db))
    return await service.reindex_all(items)


@router.get("/search", response_model=List[VectorSearchResult], dependencies=[require_vector_read])
async def search_vectors(
    query: str = Query(min_length=1, description="Search query string"),
    top_k: int = Query(default=10, ge=1, le=100),
    workspace: Optional[str] = Query(default=None),
    project: Optional[str] = Query(default=None),
    threshold: float = Query(default=0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Performs semantic vector search."""
    service = VectorSearchService(repository=VectorRepository(db))
    return await service.search(query, top_k=top_k, workspace=workspace, project=project, threshold=threshold)


@router.get("/similar", response_model=List[VectorSearchResult], dependencies=[require_vector_read])
async def get_similar_candidates(
    text: str = Query(min_length=1, description="Target comparison text"),
    top_k: int = Query(default=5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Finds top-K similar text candidates."""
    service = VectorSearchService(repository=VectorRepository(db))
    return await service.search(text, top_k=top_k)


@router.get("/statistics", response_model=VectorStatisticsResponse, dependencies=[require_vector_read])
async def get_vector_statistics(db: AsyncSession = Depends(get_db)) -> Any:
    """Returns vector database telemetry statistics."""
    service = StatisticsService(repository=VectorRepository(db))
    return await service.get_statistics()


@router.get("/health", response_model=VectorHealthResponse, dependencies=[require_vector_read])
async def get_vector_health(db: AsyncSession = Depends(get_db)) -> Any:
    """Runs vector database diagnostic health checks."""
    service = StatisticsService(repository=VectorRepository(db))
    return await service.check_health()
