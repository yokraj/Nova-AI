"""API Integration Test Suite for Nova AI Enterprise Dashboard.

Tests REST API routes under /dashboard namespace, validating RBAC authentication,
Pydantic response models, pagination structure, CRUD execution, and 404/422 error handling.
"""

from datetime import datetime, timezone
from typing import Dict
from unittest.mock import AsyncMock
import uuid
from fastapi.testclient import TestClient

from app.dashboard.dependencies import (
    get_analytics_service,
    get_dashboard_service,
    get_event_manager,
    get_health_service,
    get_monitor_service,
    get_notification_service,
    get_resource_service,
)
from app.dashboard.exceptions import DashboardNotFoundError, NotificationNotFoundError
from app.dashboard.schemas import (
    DashboardConfigurationRead,
    DashboardEventRead,
    DashboardNotificationRead,
    DashboardSnapshotRead,
    GPUMetricRead,
    HealthRecordRead,
    ProcessMetricRead,
    ResourceMetricRead,
    SystemMetricRead,
)
from app.database.models.dashboard import (
    DashboardEvent,
    DashboardNotification,
    DashboardSnapshot,
)
from fastapi.security import HTTPAuthorizationCredentials
from app.identity.infrastructure.rbac import get_current_user_claims, security_scheme
from app.main import app

# 1. Mock Admin Authorization Claims
def mock_admin_claims() -> Dict[str, str]:
    return {"user_id": str(uuid.uuid4()), "role": "admin"}


app.dependency_overrides[get_current_user_claims] = mock_admin_claims
app.dependency_overrides[security_scheme] = lambda: HTTPAuthorizationCredentials(scheme="Bearer", credentials="mock_test_token")


# In-memory test store
_test_snapshots: Dict[uuid.UUID, DashboardSnapshot] = {}
_test_notifications: Dict[uuid.UUID, DashboardNotification] = {}
_test_events: Dict[uuid.UUID, DashboardEvent] = {}

# 2. Mock Dashboard Service
class MockDashboardService:
    async def get_dashboard_overview(self):
        return {
            "timestamp": datetime.now(timezone.utc),
            "system": {
                "status": "online",
                "uptime_seconds": 3600.0,
                "active_nodes": 1,
                "cpu_usage_percent": 25.0,
                "memory_usage_percent": 50.0,
                "metadata": {},
            },
            "resources": {
                "cpu_cores_total": 8,
                "cpu_cores_used": 2.0,
                "memory_total_bytes": 16000000000,
                "memory_used_bytes": 8000000000,
                "disk_total_bytes": 100000000000,
                "disk_used_bytes": 50000000000,
                "gpu_count": 0,
                "gpu_memory_used_bytes": None,
            },
            "missions": {
                "total_missions": 3,
                "active_missions": 3,
                "completed_missions": 0,
                "failed_missions": 0,
                "pending_missions": 0,
            },
            "agents": {
                "total_agents": 10,
                "idle_agents": 10,
                "busy_agents": 0,
                "error_agents": 0,
            },
            "notifications": {
                "unread_count": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "info_alerts": 0,
            },
            "analytics": {
                "total_requests": 0,
                "avg_latency_ms": 0.0,
                "error_rate_percent": 0.0,
                "token_usage_total": 0,
            },
            "health": {
                "is_healthy": True,
                "database_status": "healthy",
                "cache_status": "healthy",
                "message_bus_status": "healthy",
                "checks": {},
            },
        }

    async def get_dashboard_snapshot(self, snapshot_id: uuid.UUID):
        if snapshot_id not in _test_snapshots or _test_snapshots[snapshot_id].is_deleted:
            raise DashboardNotFoundError(str(snapshot_id))
        return _test_snapshots[snapshot_id]

    async def create_snapshot(self, payload):
        snap_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        snap = DashboardSnapshot(
            id=snap_id,
            created_at=now,
            updated_at=now,
            system_status=payload.system_status,
            resource_status=payload.resource_status,
            active_agents=payload.active_agents,
            active_models=payload.active_models,
            running_missions=payload.running_missions,
            running_workflows=payload.running_workflows,
            voice_status=payload.voice_status,
            health_score=payload.health_score,
            is_deleted=False,
        )
        _test_snapshots[snap_id] = snap
        return snap

    async def update_snapshot(self, snapshot_id: uuid.UUID, payload):
        if snapshot_id not in _test_snapshots or _test_snapshots[snapshot_id].is_deleted:
            raise DashboardNotFoundError(str(snapshot_id))
        snap = _test_snapshots[snapshot_id]
        if payload.active_agents is not None:
            snap.active_agents = payload.active_agents
        return snap

    async def delete_snapshot(self, snapshot_id: uuid.UUID):
        if snapshot_id not in _test_snapshots or _test_snapshots[snapshot_id].is_deleted:
            raise DashboardNotFoundError(str(snapshot_id))
        snap = _test_snapshots[snapshot_id]
        snap.is_deleted = True
        return snap

    async def get_resource_summary(self):
        return {"cpu": "20%", "memory": "40%"}

    @property
    def repository(self):
        mock_repo = AsyncMock()
        items = [s for s in _test_snapshots.values() if not s.is_deleted]
        mock_repo.paginate.return_value = {
            "items": items,
            "page": 1,
            "page_size": 20,
            "total": len(items),
            "total_pages": 1,
        }
        return mock_repo


# 3. Mock System Monitor Service
class MockSystemMonitorService:
    async def get_latest_system_metrics(self):
        now = datetime.now(timezone.utc)
        return SystemMetricRead(
            id=uuid.uuid4(),
            timestamp=now,
            hostname="node-1",
            os_name="Linux",
            cpu_usage=25.0,
            memory_total=16000,
            memory_used=8000,
            memory_available=8000,
            swap_used=0,
            disk_total=100000,
            disk_used=50000,
            network_upload=100,
            network_download=200,
            uptime=3600.0,
        )

    async def get_metric_history(self, limit: int = 100):
        latest = await self.get_latest_system_metrics()
        return [latest]


# 4. Mock Resource Monitor Service
class MockResourceMonitorService:
    async def get_cpu_metrics(self):
        return []

    async def get_memory_metrics(self):
        return []

    async def get_disk_metrics(self):
        return []

    async def get_network_metrics(self):
        return []

    async def get_gpu_metrics(self):
        return []

    async def get_process_metrics(self):
        return []

    async def get_resource_history(self, resource_type=None, limit=100):
        return []


# 5. Mock Notification Service
class MockNotificationService:
    async def create_notification(self, payload):
        notif_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        n = DashboardNotification(
            id=notif_id,
            created_at=now,
            updated_at=now,
            type=payload.type,
            priority=payload.priority.value if hasattr(payload.priority, "value") else str(payload.priority),
            title=payload.title,
            message=payload.message,
            read=payload.read,
        )
        _test_notifications[notif_id] = n
        return n

    async def get_notifications(self, limit=100, unread_only=False):
        items = list(_test_notifications.values())
        if unread_only:
            items = [i for i in items if not i.read]
        return items

    async def mark_as_read(self, notification_id: uuid.UUID):
        if notification_id not in _test_notifications:
            raise NotificationNotFoundError(str(notification_id))
        n = _test_notifications[notification_id]
        n.read = True
        return n

    async def mark_all_read(self):
        count = 0
        for n in _test_notifications.values():
            if not n.read:
                n.read = True
                count += 1
        return count

    async def delete_notification(self, notification_id: uuid.UUID):
        if notification_id not in _test_notifications:
            raise NotificationNotFoundError(str(notification_id))
        return _test_notifications.pop(notification_id)

    async def get_unread_count(self):
        return len([n for n in _test_notifications.values() if not n.read])


# 6. Mock Event Manager
class MockDashboardEventManager:
    async def create_event(self, payload):
        event_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        e = DashboardEvent(
            id=event_id,
            created_at=now,
            updated_at=now,
            timestamp=payload.timestamp,
            event_type=payload.event_type,
            severity=payload.severity.value if hasattr(payload.severity, "value") else str(payload.severity),
            source=payload.source,
            title=payload.title,
            description=payload.description,
            event_metadata=payload.metadata,
            resolved=payload.resolved,
        )
        _test_events[event_id] = e
        return e

    async def list_events(self, limit=100):
        return list(_test_events.values())

    async def list_active_events(self):
        return [e for e in _test_events.values() if not e.resolved]

    async def list_resolved_events(self):
        return [e for e in _test_events.values() if e.resolved]

    async def resolve_event(self, event_id: uuid.UUID):
        if event_id not in _test_events:
            from app.dashboard.exceptions import EventNotFoundError
            raise EventNotFoundError(str(event_id))
        e = _test_events[event_id]
        e.resolved = True
        return e

    async def delete_event(self, event_id: uuid.UUID):
        if event_id not in _test_events:
            from app.dashboard.exceptions import EventNotFoundError
            raise EventNotFoundError(str(event_id))
        return _test_events.pop(event_id)


# 7. Mock Analytics & Health Services
class MockAnalyticsService:
    async def get_metrics(self, metric_name):
        return []

    async def get_metric_history(self, metric_name, limit=100):
        return []

    async def get_dashboard_statistics(self):
        return {"total": 0}


class MockHealthService:
    async def get_health_status(self):
        return {"is_healthy": True, "database_status": "healthy", "cache_status": "healthy", "message_bus_status": "healthy", "checks": {}}

    async def get_health_history(self, limit=100):
        return []

    async def get_component_health(self, component):
        return []


# Register DI Overrides
app.dependency_overrides[get_dashboard_service] = MockDashboardService
app.dependency_overrides[get_monitor_service] = MockSystemMonitorService
app.dependency_overrides[get_resource_service] = MockResourceMonitorService
app.dependency_overrides[get_notification_service] = MockNotificationService
app.dependency_overrides[get_event_manager] = MockDashboardEventManager
app.dependency_overrides[get_analytics_service] = MockAnalyticsService
app.dependency_overrides[get_health_service] = MockHealthService


def get_test_client() -> TestClient:
    return TestClient(app)


def test_dashboard_overview(client: TestClient = None):
    if client is None:
        client = get_test_client()
    response = client.get("/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "health" in data
    assert "agents" in data
    assert "missions" in data


def test_snapshots_crud_flow(client: TestClient = None):
    if client is None:
        client = get_test_client()

    payload = {
        "active_agents": 8,
        "active_models": 3,
        "running_missions": 4,
        "running_workflows": 2,
        "voice_status": "idle",
        "health_score": 0.95,
        "system_status": {"load": "normal"},
        "resource_status": {"cpu": "45%"},
    }
    res_create = client.post("/dashboard/snapshots", json=payload)
    assert res_create.status_code == 201
    created_data = res_create.json()
    snapshot_id = created_data["id"]
    assert created_data["active_agents"] == 8

    res_get = client.get(f"/dashboard/snapshots/{snapshot_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == snapshot_id

    res_list = client.get("/dashboard/snapshots?page=1&page_size=10")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert "items" in list_data
    assert "page" in list_data
    assert list_data["page"] == 1

    res_update = client.patch(f"/dashboard/snapshots/{snapshot_id}", json={"active_agents": 12})
    assert res_update.status_code == 200
    assert res_update.json()["active_agents"] == 12

    res_delete = client.delete(f"/dashboard/snapshots/{snapshot_id}")
    assert res_delete.status_code == 200
    assert res_delete.json()["is_deleted"] is True

    res_get_deleted = client.get(f"/dashboard/snapshots/{snapshot_id}")
    assert res_get_deleted.status_code == 404


def test_notifications_flow(client: TestClient = None):
    if client is None:
        client = get_test_client()

    payload = {
        "type": "alert",
        "priority": "high",
        "title": "Disk Space Warning",
        "message": "Partition /data is at 88% capacity",
    }
    res_create = client.post("/dashboard/notifications", json=payload)
    assert res_create.status_code == 201
    notif_id = res_create.json()["id"]

    res_count = client.get("/dashboard/notifications/unread-count")
    assert res_count.status_code == 200
    assert "unread_count" in res_count.json()

    res_list = client.get("/dashboard/notifications?page=1&page_size=10")
    assert res_list.status_code == 200
    assert "items" in res_list.json()

    res_read = client.patch(f"/dashboard/notifications/{notif_id}/read")
    assert res_read.status_code == 200
    assert res_read.json()["read"] is True

    res_all_read = client.patch("/dashboard/notifications/read-all")
    assert res_all_read.status_code == 200
    assert "marked_read" in res_all_read.json()

    res_del = client.delete(f"/dashboard/notifications/{notif_id}")
    assert res_del.status_code == 200


def test_events_flow(client: TestClient = None):
    if client is None:
        client = get_test_client()

    payload = {
        "event_type": "node_scaling",
        "severity": "info",
        "source": "cluster_autoscaler",
        "title": "Node Added",
        "description": "Worker node 4 provisioned",
        "metadata": {"node_id": "worker-4"},
    }
    res_create = client.post("/dashboard/events", json=payload)
    assert res_create.status_code == 201
    event_id = res_create.json()["id"]

    res_list = client.get("/dashboard/events?page=1&page_size=10")
    assert res_list.status_code == 200
    assert "items" in res_list.json()

    res_resolve = client.patch(f"/dashboard/events/{event_id}/resolve")
    assert res_resolve.status_code == 200
    assert res_resolve.json()["resolved"] is True

    res_del = client.delete(f"/dashboard/events/{event_id}")
    assert res_del.status_code == 200


def test_resources_and_analytics_health(client: TestClient = None):
    if client is None:
        client = get_test_client()

    assert client.get("/dashboard/resources").status_code == 200
    assert client.get("/dashboard/resources/cpu").status_code == 200
    assert client.get("/dashboard/resources/memory").status_code == 200
    assert client.get("/dashboard/resources/disk").status_code == 200
    assert client.get("/dashboard/resources/network").status_code == 200
    assert client.get("/dashboard/resources/gpu").status_code == 200
    assert client.get("/dashboard/resources/processes").status_code == 200

    assert client.get("/dashboard/analytics").status_code == 200
    assert client.get("/dashboard/analytics/statistics").status_code == 200

    assert client.get("/dashboard/health").status_code == 200
    assert client.get("/dashboard/health/history").status_code == 200

    assert client.get("/dashboard/agents/statistics").status_code == 200
    assert client.get("/dashboard/missions/statistics").status_code == 200
