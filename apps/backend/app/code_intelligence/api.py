"""Code Intelligence REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for repository indexing, summaries, architecture patterns,
dependency graphs, symbols, REST APIs, database schemas, and health diagnostics, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.code_intelligence.repository import CodeIntelligenceRepository
from app.code_intelligence.service import (
    RepositoryService,
    CodeAnalysisService,
    DependencyService,
    ArchitectureService,
    SummaryService,
)
from app.code_intelligence.schemas import (
    RepositoryIndexRequest,
    RepositoryResponse,
    CodeSymbolResponse,
    ArchitecturePatternResponse,
    APISchemaResponse,
    DatabaseSchemaResponse,
    RepositorySummaryResponse,
    CodeHealthResponse,
)

router = APIRouter(prefix="/api/v1/repositories", tags=["Enterprise Code Intelligence"])

# Permission dependencies
require_repo_read = Depends(PermissionChecker("repository:read"))
require_repo_write = Depends(PermissionChecker("repository:write"))
require_repo_admin = Depends(PermissionChecker("repository:admin"))


@router.post("/index", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_repo_write])
async def index_repository(request: RepositoryIndexRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Indexes source code repository structure and symbols."""
    service = RepositoryService(repository=CodeIntelligenceRepository(db))
    return await service.index_repository(request)


@router.get("", response_model=List[RepositoryResponse], dependencies=[require_repo_read])
async def list_repositories(db: AsyncSession = Depends(get_db)) -> Any:
    """Lists all registered repositories."""
    service = RepositoryService(repository=CodeIntelligenceRepository(db))
    return await service.list_repositories()


@router.get("/{repository_id}", response_model=RepositoryResponse, dependencies=[require_repo_read])
async def get_repository(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Fetches repository metadata by ID."""
    service = RepositoryService(repository=CodeIntelligenceRepository(db))
    res = await service.get_repository(repository_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Repository '{repository_id}' not found.")
    return res


@router.get("/{repository_id}/summary", response_model=RepositorySummaryResponse, dependencies=[require_repo_read])
async def get_repository_summary(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Generates executive architectural summary for a repository."""
    service = SummaryService(repository=CodeIntelligenceRepository(db))
    res = await service.get_summary(repository_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Repository '{repository_id}' not found.")
    return res


@router.get("/{repository_id}/architecture", response_model=List[ArchitecturePatternResponse], dependencies=[require_repo_read])
async def get_repository_architecture(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Extracts software architectural patterns for a repository."""
    service = ArchitectureService(repository=CodeIntelligenceRepository(db))
    return await service.get_architecture(repository_id)


@router.get("/{repository_id}/dependencies", dependencies=[require_repo_read])
async def get_repository_dependencies(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Analyzes dependency graph for a repository."""
    service = DependencyService(repository=CodeIntelligenceRepository(db))
    return await service.get_dependencies(repository_id)


@router.get("/{repository_id}/symbols", response_model=List[CodeSymbolResponse], dependencies=[require_repo_read])
async def get_repository_symbols(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Fetches symbols indexed for a repository."""
    service = CodeAnalysisService(repository=CodeIntelligenceRepository(db))
    return await service.get_symbols(repository_id)


@router.get("/{repository_id}/apis", response_model=List[APISchemaResponse], dependencies=[require_repo_read])
async def get_repository_apis(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Extracts REST API endpoints for a repository."""
    service = CodeAnalysisService(repository=CodeIntelligenceRepository(db))
    return await service.get_apis(repository_id)


@router.get("/{repository_id}/database", response_model=List[DatabaseSchemaResponse], dependencies=[require_repo_read])
async def get_repository_database(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Extracts ORM models and database tables for a repository."""
    service = CodeAnalysisService(repository=CodeIntelligenceRepository(db))
    return await service.get_database_schemas(repository_id)


@router.get("/{repository_id}/health", response_model=CodeHealthResponse, dependencies=[require_repo_read])
async def get_repository_health(repository_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Runs code intelligence diagnostic health checks."""
    service = SummaryService(repository=CodeIntelligenceRepository(db))
    return await service.check_health()
