"""Enterprise Dashboard Chaos Resilience Test Suite.

Simulates database disconnection, WebSocket connection dropouts, collector timeouts,
and partial service failures to verify graceful degradation.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.analytics_engine import AnalyticsEngine
from app.live_metrics import LiveMetricsEngine
from app.monitoring import SystemMonitoringEngine
from app.notification_engine import NotificationDeliveryManager, NotificationEngine
from app.websocket import ConnectionManager, DashboardBroadcaster, SubscriptionManager


@pytest.mark.asyncio
async def test_websocket_subscriber_disconnect_chaos():
    """Simulates abrupt client disconnects during broadcast without crashing broadcaster."""
    conn_mgr = ConnectionManager()
    sub_mgr = conn_mgr.subscription_manager
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    # Setup connection
    mock_ws = AsyncMock()
    mock_ws.send_json = AsyncMock(side_effect=RuntimeError("Connection closed abruptly"))
    from app.websocket import WebSocketConnection
    conn = WebSocketConnection(websocket=mock_ws, user_id="chaos-user")
    await conn_mgr.connect(conn)
    sub_mgr.subscribe(conn, "dashboard")

    # Broadcasting to dead connection should handle exception gracefully without raising
    await conn_mgr.broadcast_to_channel("dashboard", {"data": 123})


@pytest.mark.asyncio
async def test_monitoring_collector_failure_resilience():
    """Simulates hardware metrics collector failure returning None fallback safely."""
    engine = SystemMonitoringEngine(
        system_service=MagicMock(),
        resource_service=MagicMock(),
        health_service=MagicMock(),
        dashboard_service=MagicMock(),
    )

    # Force error in internal collection service
    engine.system_service.record_system_metrics = AsyncMock(side_effect=RuntimeError("Hardware sensor offline"))

    # Collecting now should handle error and return None fallback safely
    metric = await engine.collect_system_metrics()
    assert metric is None
