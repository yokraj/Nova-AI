"""Context Engine REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for context package building, optimization,
compression, telemetry statistics, and health diagnostics, guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.context_engine.repository import ContextEngineRepository
from app.context_engine.service import (
    ContextAssemblyService,
    CompressionService,
    StatisticsService,
)
from app.context_engine.schemas import (
    ContextBuildRequest,
    ContextBuildResponse,
    ContextOptimizeRequest,
    ContextCompressRequest,
    ContextHealthResponse,
    ContextStatisticsResponse,
)

router = APIRouter(prefix="/api/v1/context", tags=["Enterprise Context Engine"])

# Permission dependencies
require_context_read = Depends(PermissionChecker("context:read"))
require_context_write = Depends(PermissionChecker("context:write"))
require_context_admin = Depends(PermissionChecker("context:admin"))


@router.post("/build", response_model=ContextBuildResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_context_write])
async def build_context(request: ContextBuildRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Assembles and optimizes unified LLM context package."""
    service = ContextAssemblyService(repository=ContextEngineRepository(db))
    return await service.build_context(request)


@router.post("/optimize", status_code=status.HTTP_200_OK, dependencies=[require_context_write])
async def optimize_context(request: ContextOptimizeRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Optimizes raw context text fitting within token budget."""
    service = ContextAssemblyService(repository=ContextEngineRepository(db))
    candidates = [{"content": request.raw_context, "confidence": 0.9}]
    return service.optimizer.optimize_candidates(candidates, token_budget=request.token_budget)


@router.post("/compress", status_code=status.HTTP_200_OK, dependencies=[require_context_write])
async def compress_context(request: ContextCompressRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Compresses context text to target ratio."""
    service = CompressionService(repository=ContextEngineRepository(db))
    return service.compress_context(request)


@router.get("/statistics", response_model=ContextStatisticsResponse, dependencies=[require_context_read])
async def get_context_statistics(db: AsyncSession = Depends(get_db)) -> Any:
    """Returns context engine telemetry statistics."""
    service = StatisticsService(repository=ContextEngineRepository(db))
    return await service.get_statistics()


@router.get("/health", response_model=ContextHealthResponse, dependencies=[require_context_read])
async def get_context_health(db: AsyncSession = Depends(get_db)) -> Any:
    """Runs context engine diagnostic health checks."""
    service = StatisticsService(repository=ContextEngineRepository(db))
    return await service.check_health()
