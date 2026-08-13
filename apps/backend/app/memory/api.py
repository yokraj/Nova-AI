"""Memory REST API Endpoints Module.

Provides OpenAPI-compliant endpoints for Memory CRUD, searching, workspace isolation,
project memories, archival/pinning, and statistics guarded by RBAC permissions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker
from app.memory.repository import MemoryRepository
from app.memory.service import (
    MemoryService,
    WorkspaceMemoryService,
    ProjectMemoryService,
)
from app.memory.schemas import (
    MemoryEntryCreate,
    MemoryEntryUpdate,
    MemoryEntryResponse,
    MemoryStatisticsSchema,
)

router = APIRouter(prefix="/api/v1/memory", tags=["Enterprise Memory"])

# Permission dependencies
require_memory_read = Depends(PermissionChecker("memory:read"))
require_memory_write = Depends(PermissionChecker("memory:write"))
require_memory_admin = Depends(PermissionChecker("memory:admin"))


@router.post("", response_model=MemoryEntryResponse, status_code=status.HTTP_201_CREATED, dependencies=[require_memory_write])
async def create_memory(schema: MemoryEntryCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """Creates a new memory entry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.create_memory(schema)


@router.get("/search", response_model=List[MemoryEntryResponse], dependencies=[require_memory_read])
async def search_memories(
    query: str = Query(default="", description="Search query string"),
    workspace: Optional[str] = Query(default=None, description="Filter by workspace"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Searches memory entries using multi-criteria query matching."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.search(query=query, workspace=workspace, limit=limit)


@router.get("/statistics", response_model=MemoryStatisticsSchema, dependencies=[require_memory_read])
async def get_memory_statistics(db: AsyncSession = Depends(get_db)) -> Any:
    """Returns platform memory statistics telemetry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.get_statistics()


@router.get("/workspaces/{workspace_name}", dependencies=[require_memory_read])
async def get_workspace_memories(workspace_name: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Retrieves memories scoped strictly to target workspace partition."""
    ws_service = WorkspaceMemoryService(repository=MemoryRepository(db))
    return await ws_service.get_workspace_memories(workspace_name)


@router.get("/projects/{project_name}", dependencies=[require_memory_read])
async def get_project_memories(project_name: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Retrieves project architectural summary and memories."""
    pj_service = ProjectMemoryService(repository=MemoryRepository(db))
    return await pj_service.get_summary(project_name)


@router.get("/{memory_id}", response_model=MemoryEntryResponse, dependencies=[require_memory_read])
async def get_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Fetches memory entry by ID."""
    service = MemoryService(repository=MemoryRepository(db))
    res = await service.get_memory(memory_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")
    return res


@router.put("/{memory_id}", response_model=MemoryEntryResponse, dependencies=[require_memory_write])
async def update_memory(memory_id: str, schema: MemoryEntryUpdate, db: AsyncSession = Depends(get_db)) -> Any:
    """Updates fields of an existing memory entry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.update_memory(memory_id, schema)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_memory_write])
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Deletes memory entry by ID."""
    service = MemoryService(repository=MemoryRepository(db))
    deleted = await service.delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Memory '{memory_id}' not found.")


@router.post("/{memory_id}/archive", response_model=MemoryEntryResponse, dependencies=[require_memory_write])
async def archive_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Archives memory entry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.archive_memory(memory_id)


@router.post("/{memory_id}/pin", response_model=MemoryEntryResponse, dependencies=[require_memory_write])
async def pin_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Pins memory entry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.pin_memory(memory_id)


@router.post("/{memory_id}/restore", response_model=MemoryEntryResponse, dependencies=[require_memory_write])
async def restore_memory(memory_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    """Restores archived memory entry."""
    service = MemoryService(repository=MemoryRepository(db))
    return await service.restore_memory(memory_id)
