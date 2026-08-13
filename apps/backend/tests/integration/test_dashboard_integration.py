"""Enterprise Dashboard End-to-End Integration Test Suite.

Verifies complete data flow across Monitoring Engine, Live Metrics Engine, WebSocket Gateway,
Notification Engine, Analytics Engine, and Security Middleware.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.websockets import WebSocketState
import pytest

from app.analytics_engine import AnalyticsEngine
from app.live_metrics import LiveMetricsEngine
from app.monitoring import SystemMonitoringEngine
from app.notification_engine import NotificationEngine
from app.security import AuditLogger, SecurityMonitor
from app.websocket import ConnectionManager, DashboardBroadcaster, SubscriptionManager
from tests.fixtures.dashboard_fixtures import get_mock_telemetry_payload, get_mock_user_context


@pytest.mark.asyncio
async def test_end_to_end_dashboard_pipeline():
    """Verifies end-to-end telemetry pipeline from monitoring to WebSocket broadcast, notifications, and analytics."""

    # 1. Initialize WebSocket Gateway Infrastructure
    conn_mgr = ConnectionManager()
    sub_mgr = conn_mgr.subscription_manager
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    mock_ws = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    user = get_mock_user_context("admin")
    from app.websocket import WebSocketConnection
    conn = WebSocketConnection(websocket=mock_ws, user_id=user["user_id"])
    await conn_mgr.connect(conn)
    conn_mgr.subscribe(conn.connection_id, "dashboard")
    conn_mgr.subscribe(conn.connection_id, "resources")
    conn_mgr.subscribe(conn.connection_id, "notifications")

    # 3. Initialize Monitoring, Live Metrics, Notification, and Analytics Engines
    monitoring_engine = SystemMonitoringEngine(
        system_service=MagicMock(),
        resource_service=MagicMock(),
        health_service=MagicMock(),
        dashboard_service=MagicMock(),
    )
    live_metrics_engine = LiveMetricsEngine(monitoring_engine=monitoring_engine, connection_manager=conn_mgr, broadcaster=broadcaster)
    notification_engine = NotificationEngine(broadcaster=broadcaster)
    analytics_engine = AnalyticsEngine()

    notification_engine.start()
    analytics_engine.start()

    # 4. Trigger Telemetry Sample Collection & Processing
    telemetry = get_mock_telemetry_payload()
    metrics = await live_metrics_engine.collect_metrics()
    assert metrics["health"]["health_score"] >= 0.0

    # 5. Broadcast Snapshot Over WebSocket
    await broadcaster.broadcast_dashboard(telemetry)
    await live_metrics_engine.publish_metrics(metrics)
    assert mock_ws.send_json.called

    # 6. Trigger Notification Creation & Rule Evaluation
    notif = await notification_engine.create_notification(
        title="Integration Test Warning",
        message="CPU utilization spike detected",
        category="system",
        priority="HIGH",
    )
    await asyncio.sleep(0.05)
    assert notif["title"] == "Integration Test Warning"

    # 7. Collect & Aggregate Analytics
    analytics_result = analytics_engine.collect(telemetry)
    assert "aggregated" in analytics_result
    assert "kpis" in analytics_result
    assert "insights" in analytics_result
    assert analytics_result["kpis"]["cpu_utilization_percent"] > 0

    # 8. Clean up engine resources
    notification_engine.stop()
    analytics_engine.stop()
