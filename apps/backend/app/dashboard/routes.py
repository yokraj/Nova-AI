"""Dashboard REST API Router Module.

Exposes production-grade REST API endpoints for Nova AI Enterprise Dashboard,
handling snapshots, system metrics, hardware resources, notifications, events,
analytics, health diagnostics, agent workforce, missions, and configuration settings.

All route handlers act strictly as thin controllers communicating via service layer
providers and enforcing RBAC authorization claims.
"""

import math
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
import structlog

from app.dashboard.dependencies import (
    get_analytics_service,
    get_dashboard_service,
    get_event_manager,
    get_health_service,
    get_monitor_service,
    get_notification_service,
    get_resource_service,
)
from app.dashboard.repositories import ConfigurationRepository
from app.dashboard.schemas import (
    AgentSummary,
    AnalyticsRecordRead,
    AnalyticsSummary,
    DashboardConfigurationCreate,
    DashboardConfigurationRead,
    DashboardConfigurationUpdate,
    DashboardEventCreate,
    DashboardEventRead,
    DashboardNotificationCreate,
    DashboardNotificationRead,
    DashboardOverview,
    DashboardSnapshotCreate,
    DashboardSnapshotRead,
    DashboardSnapshotUpdate,
    GPUMetricRead,
    HealthRecordRead,
    HealthSummary,
    MissionSummary,
    NotificationSummary,
    PaginatedResponse,
    ProcessMetricRead,
    ResourceMetricRead,
    ResourceStatus,
    SystemMetricRead,
    SystemStatus,
)
from app.dashboard.services import (
    AgentDashboardService,
    AnalyticsService,
    DashboardEventManager,
    DashboardService,
    HealthService,
    MissionDashboardService,
    NotificationService,
    ResourceMonitorService,
    SystemMonitorService,
)
from app.database.models.dashboard import DashboardConfiguration
from app.database.session import get_db
from app.identity.infrastructure.rbac import PermissionChecker

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ---------------------------------------------------------------------------
# 1. Dashboard Overview & Snapshots
# ---------------------------------------------------------------------------

@router.get(
    "/overview",
    response_model=DashboardOverview,
    summary="Get Consolidated Dashboard Overview",
    description="Returns high-level system overview telemetry, active agent/mission counters, and status.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_overview(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/overview controller."""
    logger.info("request_get_dashboard_overview")
    return await dashboard_service.get_dashboard_overview()


@router.get(
    "/snapshots",
    response_model=PaginatedResponse[DashboardSnapshotRead],
    summary="List Dashboard Snapshots",
    description="Retrieves a paginated collection of historical dashboard state snapshots.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def list_snapshots(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/snapshots controller."""
    logger.info("request_list_snapshots", page=page, page_size=page_size)
    paginated = await dashboard_service.repository.paginate(page=page, page_size=page_size)
    return PaginatedResponse[DashboardSnapshotRead](
        items=paginated["items"],
        page=paginated["page"],
        page_size=paginated["page_size"],
        total=paginated["total"],
        pages=paginated["total_pages"],
    )


@router.get(
    "/snapshots/{snapshot_id}",
    response_model=DashboardSnapshotRead,
    summary="Get Dashboard Snapshot Details",
    description="Retrieves a specific dashboard snapshot by its unique UUID identifier.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_snapshot(
    snapshot_id: uuid.UUID,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/snapshots/{snapshot_id} controller."""
    logger.info("request_get_snapshot", snapshot_id=str(snapshot_id))
    return await dashboard_service.get_dashboard_snapshot(snapshot_id)


@router.post(
    "/snapshots",
    response_model=DashboardSnapshotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Dashboard Snapshot",
    description="Persists a new snapshot record of dashboard state.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def create_snapshot(
    payload: DashboardSnapshotCreate,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """POST /dashboard/snapshots controller."""
    logger.info("request_create_snapshot", active_agents=payload.active_agents)
    snapshot = await dashboard_service.create_snapshot(payload)
    logger.info("success_create_snapshot", snapshot_id=str(snapshot.id))
    return snapshot


@router.patch(
    "/snapshots/{snapshot_id}",
    response_model=DashboardSnapshotRead,
    summary="Update Dashboard Snapshot",
    description="Updates specific attributes of an existing dashboard snapshot.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def update_snapshot(
    snapshot_id: uuid.UUID,
    payload: DashboardSnapshotUpdate,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """PATCH /dashboard/snapshots/{snapshot_id} controller."""
    logger.info("request_update_snapshot", snapshot_id=str(snapshot_id))
    updated = await dashboard_service.update_snapshot(snapshot_id, payload)
    logger.info("success_update_snapshot", snapshot_id=str(snapshot_id))
    return updated


@router.delete(
    "/snapshots/{snapshot_id}",
    response_model=DashboardSnapshotRead,
    summary="Delete Dashboard Snapshot",
    description="Soft-deletes a dashboard snapshot by its unique UUID identifier.",
    dependencies=[Depends(PermissionChecker("dashboard:admin"))],
)
async def delete_snapshot(
    snapshot_id: uuid.UUID,
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """DELETE /dashboard/snapshots/{snapshot_id} controller."""
    logger.info("request_delete_snapshot", snapshot_id=str(snapshot_id))
    deleted = await dashboard_service.delete_snapshot(snapshot_id)
    logger.info("success_delete_snapshot", snapshot_id=str(snapshot_id))
    return deleted


# ---------------------------------------------------------------------------
# 2. System Telemetry Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/system",
    response_model=SystemMetricRead,
    summary="Get Latest System Status",
    description="Returns the most recent system metrics sample (OS name, uptime, CPU/Memory load).",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_system_status(
    system_service: SystemMonitorService = Depends(get_monitor_service),
) -> Any:
    """GET /dashboard/system controller."""
    logger.info("request_get_system_status")
    return await system_service.get_latest_system_metrics()


@router.get(
    "/system/history",
    response_model=PaginatedResponse[SystemMetricRead],
    summary="Get System Metrics History",
    description="Retrieves a paginated list of historical system metrics samples.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_system_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    system_service: SystemMonitorService = Depends(get_monitor_service),
) -> Any:
    """GET /dashboard/system/history controller."""
    logger.info("request_get_system_history", page=page, page_size=page_size)
    history = await system_service.get_metric_history(limit=page_size * page)
    total = len(history)
    start = (page - 1) * page_size
    items = history[start : start + page_size]
    pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[SystemMetricRead](
        items=items, page=page, page_size=page_size, total=total, pages=pages
    )


# ---------------------------------------------------------------------------
# 3. Hardware Resource Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/resources",
    response_model=Dict[str, Any],
    summary="Get Resource Summary",
    description="Returns high-level hardware allocation dictionary (CPU, Memory, Storage, GPU).",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_resource_summary(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/resources controller."""
    logger.info("request_get_resource_summary")
    return await dashboard_service.get_resource_summary()


@router.get(
    "/resources/cpu",
    response_model=List[ResourceMetricRead],
    summary="Get CPU Metrics",
    description="Retrieves recent CPU core utilization metrics samples.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_cpu_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/cpu controller."""
    logger.info("request_get_cpu_metrics")
    return await resource_service.get_cpu_metrics()


@router.get(
    "/resources/memory",
    response_model=List[ResourceMetricRead],
    summary="Get Memory Metrics",
    description="Retrieves recent RAM and swap space utilization samples.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_memory_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/memory controller."""
    logger.info("request_get_memory_metrics")
    return await resource_service.get_memory_metrics()


@router.get(
    "/resources/disk",
    response_model=List[ResourceMetricRead],
    summary="Get Disk Metrics",
    description="Retrieves partition storage usage and I/O metrics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_disk_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/disk controller."""
    logger.info("request_get_disk_metrics")
    return await resource_service.get_disk_metrics()


@router.get(
    "/resources/network",
    response_model=List[ResourceMetricRead],
    summary="Get Network Metrics",
    description="Retrieves network interface upload/download throughput metrics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_network_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/network controller."""
    logger.info("request_get_network_metrics")
    return await resource_service.get_network_metrics()


@router.get(
    "/resources/gpu",
    response_model=List[GPUMetricRead],
    summary="Get GPU Metrics",
    description="Retrieves attached GPU device utilization, VRAM, and thermal metrics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_gpu_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/gpu controller."""
    logger.info("request_get_gpu_metrics")
    return await resource_service.get_gpu_metrics()


@router.get(
    "/resources/processes",
    response_model=List[ProcessMetricRead],
    summary="Get Process Metrics",
    description="Retrieves process table CPU and memory consumption metrics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_process_metrics(
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/processes controller."""
    logger.info("request_get_process_metrics")
    return await resource_service.get_process_metrics()


@router.get(
    "/resources/history",
    response_model=List[ResourceMetricRead],
    summary="Get Hardware Resource History",
    description="Retrieves historical resource metrics samples filtered by resource_type.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_resource_history(
    resource_type: Optional[str] = Query(default=None, description="Optional resource type filter (cpu, memory, disk, network)"),
    limit: int = Query(default=100, ge=1, le=500, description="Max history limit"),
    resource_service: ResourceMonitorService = Depends(get_resource_service),
) -> Any:
    """GET /dashboard/resources/history controller."""
    logger.info("request_get_resource_history", resource_type=resource_type, limit=limit)
    return await resource_service.get_resource_history(resource_type=resource_type, limit=limit)


# ---------------------------------------------------------------------------
# 4. Notifications Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/notifications",
    response_model=PaginatedResponse[DashboardNotificationRead],
    summary="List Notifications",
    description="Retrieves a paginated list of dashboard notifications with optional unread filter.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def list_notifications(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(default=False, description="Filter for unread notifications only"),
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """GET /dashboard/notifications controller."""
    logger.info("request_list_notifications", page=page, page_size=page_size, unread_only=unread_only)
    notifs = await notification_service.get_notifications(limit=1000, unread_only=unread_only)
    total = len(notifs)
    start = (page - 1) * page_size
    items = notifs[start : start + page_size]
    pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[DashboardNotificationRead](
        items=items, page=page, page_size=page_size, total=total, pages=pages
    )


@router.post(
    "/notifications",
    response_model=DashboardNotificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Notification",
    description="Creates and persists a new dashboard alert notification.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def create_notification(
    payload: DashboardNotificationCreate,
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """POST /dashboard/notifications controller."""
    logger.info("request_create_notification", title=payload.title)
    created = await notification_service.create_notification(payload)
    logger.info("success_create_notification", notification_id=str(created.id))
    return created


@router.patch(
    "/notifications/{id}/read",
    response_model=DashboardNotificationRead,
    summary="Mark Notification as Read",
    description="Marks a specific dashboard notification as read.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def mark_notification_read(
    id: uuid.UUID,
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """PATCH /dashboard/notifications/{id}/read controller."""
    logger.info("request_mark_notification_read", notification_id=str(id))
    updated = await notification_service.mark_as_read(id)
    logger.info("success_mark_notification_read", notification_id=str(id))
    return updated


@router.patch(
    "/notifications/read-all",
    response_model=Dict[str, Any],
    summary="Mark All Notifications as Read",
    description="Marks all unread dashboard notifications as read.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def mark_all_notifications_read(
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """PATCH /dashboard/notifications/read-all controller."""
    logger.info("request_mark_all_notifications_read")
    count = await notification_service.mark_all_read()
    logger.info("success_mark_all_notifications_read", count=count)
    return {"marked_read": count}


@router.delete(
    "/notifications/{id}",
    response_model=DashboardNotificationRead,
    summary="Delete Notification",
    description="Deletes a specific dashboard notification by UUID.",
    dependencies=[Depends(PermissionChecker("dashboard:admin"))],
)
async def delete_notification(
    id: uuid.UUID,
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """DELETE /dashboard/notifications/{id} controller."""
    logger.info("request_delete_notification", notification_id=str(id))
    deleted = await notification_service.delete_notification(id)
    logger.info("success_delete_notification", notification_id=str(id))
    return deleted


@router.get(
    "/notifications/unread-count",
    response_model=Dict[str, Any],
    summary="Get Unread Notification Count",
    description="Returns total number of unread alerts.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_unread_notification_count(
    notification_service: NotificationService = Depends(get_notification_service),
) -> Any:
    """GET /dashboard/notifications/unread-count controller."""
    logger.info("request_get_unread_notification_count")
    count = await notification_service.get_unread_count()
    return {"unread_count": count}


# ---------------------------------------------------------------------------
# 5. Events Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/events",
    response_model=PaginatedResponse[DashboardEventRead],
    summary="List Dashboard Events",
    description="Retrieves a paginated list of dashboard audit and warning events.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def list_events(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    resolved: Optional[bool] = Query(default=None, description="Optional resolution status filter"),
    event_manager: DashboardEventManager = Depends(get_event_manager),
) -> Any:
    """GET /dashboard/events controller."""
    logger.info("request_list_events", page=page, page_size=page_size, resolved=resolved)
    if resolved is True:
        events = await event_manager.list_resolved_events()
    elif resolved is False:
        events = await event_manager.list_active_events()
    else:
        events = await event_manager.list_events(limit=1000)

    total = len(events)
    start = (page - 1) * page_size
    items = events[start : start + page_size]
    pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[DashboardEventRead](
        items=items, page=page, page_size=page_size, total=total, pages=pages
    )


@router.post(
    "/events",
    response_model=DashboardEventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Dashboard Event",
    description="Records a new dashboard audit event or system warning log.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def create_event(
    payload: DashboardEventCreate,
    event_manager: DashboardEventManager = Depends(get_event_manager),
) -> Any:
    """POST /dashboard/events controller."""
    logger.info("request_create_event", title=payload.title, event_type=payload.event_type)
    created = await event_manager.create_event(payload)
    logger.info("success_create_event", event_id=str(created.id))
    return created


@router.patch(
    "/events/{id}/resolve",
    response_model=DashboardEventRead,
    summary="Resolve Dashboard Event",
    description="Marks an active event as resolved.",
    dependencies=[Depends(PermissionChecker("dashboard:write"))],
)
async def resolve_event(
    id: uuid.UUID,
    event_manager: DashboardEventManager = Depends(get_event_manager),
) -> Any:
    """PATCH /dashboard/events/{id}/resolve controller."""
    logger.info("request_resolve_event", event_id=str(id))
    resolved = await event_manager.resolve_event(id)
    logger.info("success_resolve_event", event_id=str(id))
    return resolved


@router.delete(
    "/events/{id}",
    response_model=DashboardEventRead,
    summary="Delete Dashboard Event",
    description="Deletes a dashboard event record.",
    dependencies=[Depends(PermissionChecker("dashboard:admin"))],
)
async def delete_event(
    id: uuid.UUID,
    event_manager: DashboardEventManager = Depends(get_event_manager),
) -> Any:
    """DELETE /dashboard/events/{id} controller."""
    logger.info("request_delete_event", event_id=str(id))
    deleted = await event_manager.delete_event(id)
    logger.info("success_delete_event", event_id=str(id))
    return deleted


# ---------------------------------------------------------------------------
# 6. Analytics Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/analytics",
    response_model=List[AnalyticsRecordRead],
    summary="Get Analytics Metrics",
    description="Retrieves analytics records matching specified metric_name.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_analytics(
    metric_name: str = Query(default="api_latency", description="Target metric name to query"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """GET /dashboard/analytics controller."""
    logger.info("request_get_analytics", metric_name=metric_name)
    return await analytics_service.get_metrics(metric_name)


@router.get(
    "/analytics/history",
    response_model=List[AnalyticsRecordRead],
    summary="Get Analytics Metric History",
    description="Retrieves historical analytics records for specified metric_name.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_analytics_history(
    metric_name: str = Query(default="api_latency", description="Target metric name"),
    limit: int = Query(default=100, ge=1, le=500, description="Max history records limit"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """GET /dashboard/analytics/history controller."""
    logger.info("request_get_analytics_history", metric_name=metric_name, limit=limit)
    return await analytics_service.get_metric_history(metric_name, limit=limit)


@router.get(
    "/analytics/statistics",
    response_model=Dict[str, Any],
    summary="Get Analytics Statistics",
    description="Returns summary statistics across analytics records.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_analytics_statistics(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """GET /dashboard/analytics/statistics controller."""
    logger.info("request_get_analytics_statistics")
    return await analytics_service.get_dashboard_statistics()


# ---------------------------------------------------------------------------
# 7. Health Diagnostics Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Get Health Summary",
    description="Returns component diagnostic statuses and overall health score.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_health_status(
    health_service: HealthService = Depends(get_health_service),
) -> Any:
    """GET /dashboard/health controller."""
    logger.info("request_get_health_status")
    return await health_service.get_health_status()


@router.get(
    "/health/history",
    response_model=List[HealthRecordRead],
    summary="Get Health Diagnostic History",
    description="Retrieves historical health check diagnostic records.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_health_history(
    limit: int = Query(default=100, ge=1, le=500, description="Max records limit"),
    health_service: HealthService = Depends(get_health_service),
) -> Any:
    """GET /dashboard/health/history controller."""
    logger.info("request_get_health_history", limit=limit)
    return await health_service.get_health_history(limit=limit)


@router.get(
    "/health/components",
    response_model=List[HealthRecordRead],
    summary="Get Component Health Records",
    description="Retrieves health check records for specified component.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_component_health(
    component: str = Query(default="database", description="Target component name"),
    health_service: HealthService = Depends(get_health_service),
) -> Any:
    """GET /dashboard/health/components controller."""
    logger.info("request_get_component_health", component=component)
    return await health_service.get_component_health(component)


# ---------------------------------------------------------------------------
# 8. Agent Workforce & Missions Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/agents",
    response_model=List[Dict[str, Any]],
    summary="Get Active Agents Summary",
    description="Returns active workforce agents.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_active_agents(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/agents controller."""
    logger.info("request_get_active_agents")
    agent_svc = AgentDashboardService(dashboard_service.repository)
    return await agent_svc.get_active_agents()


@router.get(
    "/agents/statistics",
    response_model=Dict[str, Any],
    summary="Get Agent Workforce Statistics",
    description="Returns idle, busy, and errored agent workload statistics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_agent_statistics(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/agents/statistics controller."""
    logger.info("request_get_agent_statistics")
    agent_svc = AgentDashboardService(dashboard_service.repository)
    return await agent_svc.get_agent_statistics()


@router.get(
    "/missions",
    response_model=List[Dict[str, Any]],
    summary="Get Active Missions Summary",
    description="Returns active mission execution workflows.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_active_missions(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/missions controller."""
    logger.info("request_get_active_missions")
    mission_svc = MissionDashboardService(dashboard_service.repository)
    return await mission_svc.get_active_missions()


@router.get(
    "/missions/statistics",
    response_model=Dict[str, Any],
    summary="Get Mission Runtime Statistics",
    description="Returns mission completion rates and workload statistics.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_mission_statistics(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> Any:
    """GET /dashboard/missions/statistics controller."""
    logger.info("request_get_mission_statistics")
    mission_svc = MissionDashboardService(dashboard_service.repository)
    return await mission_svc.get_mission_statistics()


# ---------------------------------------------------------------------------
# 9. Configuration Settings Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/configuration",
    response_model=DashboardConfigurationRead,
    summary="Get Dashboard Configuration",
    description="Retrieves dashboard refresh interval, cache TTL, and retention parameters.",
    dependencies=[Depends(PermissionChecker("dashboard:read"))],
)
async def get_configuration(
    session: Any = Depends(get_db),
) -> Any:
    """GET /dashboard/configuration controller."""
    logger.info("request_get_configuration")
    repo = ConfigurationRepository(session)
    configs = await repo.list(skip=0, limit=1)
    if configs:
        return configs[0]
    # Create initial default if not yet stored
    created = await repo.create(DashboardConfiguration())
    return created


@router.patch(
    "/configuration",
    response_model=DashboardConfigurationRead,
    summary="Update Dashboard Configuration",
    description="Updates dashboard refresh rate, cache TTL, and history retention limits.",
    dependencies=[Depends(PermissionChecker("dashboard:admin"))],
)
async def update_configuration(
    payload: DashboardConfigurationUpdate,
    session: Any = Depends(get_db),
) -> Any:
    """PATCH /dashboard/configuration controller."""
    logger.info("request_update_configuration")
    repo = ConfigurationRepository(session)
    configs = await repo.list(skip=0, limit=1)
    if not configs:
        created = await repo.create(DashboardConfiguration())
        target_id = created.id
    else:
        target_id = configs[0].id

    update_dict = payload.model_dump(exclude_unset=True)
    updated = await repo.update(target_id, update_dict)
    logger.info("success_update_configuration", config_id=str(target_id))
    return updated
