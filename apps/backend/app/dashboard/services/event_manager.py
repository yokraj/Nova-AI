"""Dashboard Event Manager Module.

Provides event logging, resolution tracking, active/resolved filtering,
and event deletion backed by database storage.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
import structlog

from app.dashboard.exceptions import EventNotFoundError
from app.dashboard.repositories import DashboardBaseRepository
from app.dashboard.schemas import DashboardEventCreate
from app.database.models.dashboard import DashboardEvent

logger = structlog.get_logger(__name__)


class DashboardEventManager:
    """Manager for dashboard events, audit logs, and resolution tracking."""

    def __init__(self, repository: DashboardBaseRepository[DashboardEvent]) -> None:
        self.repository = repository
        logger.info("dashboard_event_manager_initialized")

    async def create_event(self, data: DashboardEventCreate) -> DashboardEvent:
        """Creates a new dashboard event record."""
        event = DashboardEvent(
            snapshot_id=data.snapshot_id,
            timestamp=data.timestamp,
            event_type=data.event_type,
            severity=data.severity.value if hasattr(data.severity, "value") else str(data.severity),
            source=data.source,
            title=data.title,
            description=data.description,
            event_metadata=data.metadata,
            resolved=data.resolved,
            resolved_at=data.resolved_at,
        )
        created = await self.repository.create(event)
        logger.info("dashboard_event_created", event_id=str(created.id), title=data.title)
        return created

    async def resolve_event(self, event_id: uuid.UUID) -> DashboardEvent:
        """Marks a dashboard event as resolved with timestamp."""
        now = datetime.now(timezone.utc)
        updated = await self.repository.update(event_id, {"resolved": True, "resolved_at": now})
        if not updated:
            raise EventNotFoundError(str(event_id))
        logger.info("dashboard_event_resolved", event_id=str(event_id))
        return updated

    async def list_events(self, limit: int = 100) -> List[DashboardEvent]:
        """Lists historical dashboard events."""
        return await self.repository.list(skip=0, limit=limit)

    async def list_active_events(self) -> List[DashboardEvent]:
        """Lists active (unresolved) dashboard events."""
        events = await self.list_events(limit=500)
        return [e for e in events if not e.resolved]

    async def list_resolved_events(self) -> List[DashboardEvent]:
        """Lists resolved dashboard events."""
        events = await self.list_events(limit=500)
        return [e for e in events if e.resolved]

    async def delete_event(self, event_id: uuid.UUID) -> DashboardEvent:
        """Deletes a dashboard event by ID."""
        deleted = await self.repository.delete(event_id)
        if not deleted:
            raise EventNotFoundError(str(event_id))
        logger.info("dashboard_event_deleted", event_id=str(event_id))
        return deleted
