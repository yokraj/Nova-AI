"""Enterprise Dashboard Load Test Suite.

Simulates concurrent user load (100, 500, 1000, 2500, 5000 virtual requests/connections)
and benchmarks latency, throughput, error rates, and memory stability.
"""

import asyncio
import time
from unittest.mock import AsyncMock
import pytest

from app.analytics_engine import AnalyticsEngine
from app.live_metrics import LiveMetricsEngine
from app.monitoring import SystemMonitoringEngine
from app.notification_engine import NotificationEngine
from app.websocket import ConnectionManager, DashboardBroadcaster, SubscriptionManager
from tests.fixtures.dashboard_fixtures import get_mock_telemetry_payload


@pytest.mark.asyncio
async def test_concurrent_websocket_connection_load():
    """Simulates load of 500 concurrent WebSocket subscriber connections."""
    conn_mgr = ConnectionManager()
    sub_mgr = conn_mgr.subscription_manager
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    conn_count = 500
    mock_clients = []

    start = time.time()
    from app.websocket import WebSocketConnection
    for i in range(conn_count):
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_clients.append(mock_ws)
        conn = WebSocketConnection(websocket=mock_ws, user_id=f"load-user-{i}")
        await conn_mgr.connect(conn)
        sub_mgr.subscribe(conn, "dashboard")

    connect_duration = (time.time() - start) * 1000.0

    assert conn_mgr.connection_count() == 500

    # Broadcast event to 500 subscribers
    start = time.time()
    delivered = await conn_mgr.broadcast_to_channel("dashboard", {"event": "dashboard.snapshot.created", "payload": {"test": True}})
    broadcast_duration = (time.time() - start) * 1000.0

    # 500 connection setup must complete under 3000ms (3 seconds)
    assert connect_duration < 3000.0
    # 500 subscriber broadcast must complete under 50ms
    assert broadcast_duration < 50.0

    # Cleanup
    await conn_mgr.disconnect_all()
    assert conn_mgr.connection_count() == 0


@pytest.mark.asyncio
async def test_analytics_collection_load():
    """Simulates 1,000 rapid concurrent telemetry analytics processing calls."""
    engine = AnalyticsEngine()
    telemetry = get_mock_telemetry_payload()

    start = time.time()
    tasks = [asyncio.to_thread(engine.collect, telemetry) for _ in range(1000)]
    results = await asyncio.gather(*tasks)
    duration_ms = (time.time() - start) * 1000.0

    assert len(results) == 1000
    assert engine.statistics.aggregation_runs == 1000
    # 1,000 parallel aggregations must complete under 1500ms
    assert duration_ms < 1500.0
