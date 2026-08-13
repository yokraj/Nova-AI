"""Dashboard Repository Layer Module.

Provides asynchronous database repository abstractions for dashboard snapshots,
node and system metrics, analytics records, notifications, health records, and
dashboard configuration persistence.
"""

import math
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base
from app.database.models.dashboard import (
    AnalyticsRecord,
    DashboardConfiguration,
    DashboardEvent,
    DashboardNotification,
    DashboardSnapshot,
    GPUMetric,
    HealthRecord,
    ProcessMetric,
    ResourceMetric,
    SystemMetric,
)
from app.repositories.base import BaseRepository

T = TypeVar("T", bound=Base)


class DashboardBaseRepository(BaseRepository[T]):
    """Extends generic BaseRepository with standardized CRUD and pagination operations."""

    async def get_by_id(self, id: Any) -> Optional[T]:
        """Retrieves entity by primary key identifier."""
        return await self.get(id)

    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Updates attributes of an existing entity record by ID.
        
        Args:
            id: Primary key identifier.
            data: Attribute key-value dictionary to update.
            
        Returns:
            Updated model entity instance, or None if not found.
        """
        entity = await self.get(id)
        if not entity:
            return None

        for key, value in data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)

        self.session.add(entity)
        return entity

    async def paginate(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Returns paginated query result dictionary with metadata.
        
        Args:
            page: 1-indexed page number.
            page_size: Maximum items per page.
            
        Returns:
            Dict containing items list, total count, page, page_size, and total_pages.
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        skip = (page - 1) * page_size

        count_stmt = select(func.count()).select_from(self.model)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        items = await self.list(skip=skip, limit=page_size)
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }


class DashboardRepository(DashboardBaseRepository[DashboardSnapshot]):
    """Repository for managing DashboardSnapshot entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DashboardSnapshot, session)

    async def delete(self, id: Any) -> Optional[DashboardSnapshot]:
        """Soft-deletes dashboard snapshot entity by setting is_deleted=True."""
        entity = await self.get(id)
        if entity:
            entity.is_deleted = True
            self.session.add(entity)
        return entity


class MetricsRepository:
    """Repository for system, resource, GPU, and process metrics persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.system = DashboardBaseRepository(SystemMetric, session)
        self.resource = DashboardBaseRepository(ResourceMetric, session)
        self.gpu = DashboardBaseRepository(GPUMetric, session)
        self.process = DashboardBaseRepository(ProcessMetric, session)

    async def create(self, metric_entity: Any) -> Any:
        """Creates a metric record (SystemMetric, ResourceMetric, GPUMetric, or ProcessMetric)."""
        self.session.add(metric_entity)
        return metric_entity

    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[SystemMetric]:
        """Updates a SystemMetric entity by ID."""
        return await self.system.update(id, data)

    async def delete(self, id: Any) -> Optional[SystemMetric]:
        """Deletes a SystemMetric entity by ID."""
        return await self.system.delete(id)

    async def get_by_id(self, id: Any) -> Optional[SystemMetric]:
        """Gets SystemMetric entity by ID."""
        return await self.system.get(id)

    async def list(self, skip: int = 0, limit: int = 100) -> List[SystemMetric]:
        """Lists SystemMetric records."""
        return await self.system.list(skip=skip, limit=limit)

    async def paginate(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Paginates SystemMetric records."""
        return await self.system.paginate(page=page, page_size=page_size)


class AnalyticsRepository(DashboardBaseRepository[AnalyticsRecord]):
    """Repository for managing AnalyticsRecord entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AnalyticsRecord, session)


class NotificationRepository(DashboardBaseRepository[DashboardNotification]):
    """Repository for managing DashboardNotification entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DashboardNotification, session)


class HealthRepository(DashboardBaseRepository[HealthRecord]):
    """Repository for managing HealthRecord diagnostic entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(HealthRecord, session)


class ConfigurationRepository(DashboardBaseRepository[DashboardConfiguration]):
    """Repository for managing DashboardConfiguration settings entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DashboardConfiguration, session)
