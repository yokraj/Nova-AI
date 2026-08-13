"""Knowledge Graph REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for entity node creation, relationship edge creation,
graph querying, shortest path traversal, telemetry statistics, and health diagnostics, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.knowledge_graph.repository import KnowledgeGraphRepository
from app.knowledge_graph.service import (
    EntityService,
    RelationshipService,
    GraphQueryService,
    KnowledgeGraphService,
)
from app.knowledge_graph.schemas import (
    EntityCreateRequest,
    EntityResponse,
    RelationshipCreateRequest,
    RelationshipResponse,
    GraphPathResponse,
    GraphHealthResponse,
    GraphStatisticsResponse,
)

router = APIRouter(prefix="/api/v1/graph", tags=["Enterprise Knowledge Graph Engine"])

# Permission dependencies
require_graph_read = Depends(PermissionChecker("graph:read"))
require_graph_write = Depends(PermissionChecker("graph:write"))
require_graph_admin = Depends(PermissionChecker("graph:admin"))


@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_graph_write])
async def create_entity(request: EntityCreateRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Creates a new graph entity node."""
    service = EntityService(repository=KnowledgeGraphRepository(db))
    return await service.create_entity(request)


@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_graph_write])
async def create_relationship(request: RelationshipCreateRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Creates a new graph relationship edge."""
    service = RelationshipService(repository=KnowledgeGraphRepository(db))
    return await service.create_relationship(request)


@router.get("/entity/{entity_id}", response_model=EntityResponse, dependencies=[require_graph_read])
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Fetches graph entity node by ID."""
    service = EntityService(repository=KnowledgeGraphRepository(db))
    res = await service.get_entity(entity_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity '{entity_id}' not found.")
    return res


@router.get("/query", dependencies=[require_graph_read])
async def query_graph(
    q: str = Query(default="", description="Search query text"),
    workspace: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Queries entities and relationships in the knowledge graph."""
    service = GraphQueryService(repository=KnowledgeGraphRepository(db))
    return await service.query_graph(q, workspace=workspace)


@router.get("/path", response_model=GraphPathResponse, dependencies=[require_graph_read])
async def find_shortest_path(
    start_id: str = Query(description="Start entity UUID"),
    end_id: str = Query(description="End entity UUID"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculates shortest path trace between nodes."""
    service = GraphQueryService(repository=KnowledgeGraphRepository(db))
    return await service.find_shortest_path(start_id, end_id)


@router.get("/statistics", response_model=GraphStatisticsResponse, dependencies=[require_graph_read])
async def get_graph_statistics(db: AsyncSession = Depends(get_db)) -> Any:
    """Returns topological graph telemetry statistics."""
    service = KnowledgeGraphService(repository=KnowledgeGraphRepository(db))
    return await service.get_statistics()


@router.get("/health", response_model=GraphHealthResponse, dependencies=[require_graph_read])
async def get_graph_health(db: AsyncSession = Depends(get_db)) -> Any:
    """Runs graph diagnostic health checks."""
    service = KnowledgeGraphService(repository=KnowledgeGraphRepository(db))
    return await service.check_health()
