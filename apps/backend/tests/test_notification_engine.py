"""Unit and Integration Test Suite for Nova AI Enterprise Notification Engine.

Tests NotificationEngine lifecycle, RuleEngine threshold evaluation, PriorityManager,
NotificationDeduplicator fingerprinting, PriorityQueue ordering, DeliveryManager WebSocket
broadcasting, Analytics, Statistics, and Retention Cleanup.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.websockets import WebSocketState
import pytest

from app.notification_engine import (
    DuplicateNotificationError,
    NotificationAnalytics,
    NotificationCleanup,
    NotificationConfig,
    NotificationDeduplicator,
    NotificationDeliveryManager,
    NotificationEngine,
    NotificationPriorityLevel,
    NotificationPriorityManager,
    NotificationQueue,
    NotificationRuleEngine,
    NotificationStatistics,
)
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.connection import WebSocketConnection
from app.websocket.manager import ConnectionManager


def test_notification_config():
    """Test NotificationConfig initialization and threshold parameters."""
    cfg = NotificationConfig()
    assert cfg.notification_retention_days == 30
    assert cfg.max_notifications == 1000
    assert cfg.duplicate_window == 300


def test_priority_manager():
    """Test NotificationPriorityManager priority classification, escalation, and downgrade."""
    prio_mgr = NotificationPriorityManager()

    # 1. High CPU -> HIGH or URGENT
    assert prio_mgr.calculate_priority("system.cpu", {"cpu": 90.0}) == NotificationPriorityLevel.HIGH
    assert prio_mgr.calculate_priority("system.cpu", {"cpu": 98.0}) == NotificationPriorityLevel.URGENT

    # 2. Critical Event -> URGENT
    assert prio_mgr.calculate_priority("security.alert", {}) == NotificationPriorityLevel.URGENT

    # 3. Escalation & Downgrade
    assert prio_mgr.escalate(NotificationPriorityLevel.NORMAL) == NotificationPriorityLevel.HIGH
    assert prio_mgr.downgrade(NotificationPriorityLevel.HIGH) == NotificationPriorityLevel.NORMAL


def test_deduplicator():
    """Test NotificationDeduplicator fingerprint hashing and duplicate window."""
    dedup = NotificationDeduplicator(window_seconds=10.0)
    notif = {"title": "CPU High", "category": "system", "message": "CPU reached 90%"}

    assert dedup.is_duplicate(notif) is False
    dedup.register(notif)
    assert dedup.is_duplicate(notif) is True


def test_rule_engine():
    """Test NotificationRuleEngine evaluating telemetry payloads."""
    rule_engine = NotificationRuleEngine()
    assert "cpu_threshold" in rule_engine.list_rules()

    # High CPU payload matches CPU rule
    alerts = rule_engine.evaluate("system.telemetry", {"cpu_percent": 90.0})
    assert len(alerts) >= 1
    assert alerts[0]["title"] == "High CPU Utilization Alert"

    # Agent offline matches Agent rule
    agent_alerts = rule_engine.evaluate("agent.offline", {"agent_name": "Worker-1"})
    assert len(agent_alerts) >= 1
    assert "Worker-1" in agent_alerts[0]["message"]


async def test_priority_queue():
    """Test NotificationQueue priority rank ordering (URGENT before HIGH before LOW)."""
    queue = NotificationQueue()

    await queue.enqueue({"title": "Low Alert", "priority": "LOW"})
    await queue.enqueue({"title": "Urgent Alert", "priority": "URGENT"})
    await queue.enqueue({"title": "Normal Alert", "priority": "NORMAL"})

    item1 = await queue.dequeue()
    assert item1["title"] == "Urgent Alert"

    item2 = await queue.dequeue()
    assert item2["title"] == "Normal Alert"

    item3 = await queue.dequeue()
    assert item3["title"] == "Low Alert"


async def test_delivery_manager():
    """Test NotificationDeliveryManager broadcasting over WebSocket channels."""
    conn_mgr = ConnectionManager()
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_json = AsyncMock()

    conn = WebSocketConnection(websocket=mock_ws, user_id="admin-123")
    await conn_mgr.connect(conn)
    conn_mgr.subscribe(conn.connection_id, "notifications")

    delivery = NotificationDeliveryManager(broadcaster=broadcaster)

    res = await delivery.deliver_realtime({"id": "notif-1", "title": "Test Alert", "priority": "NORMAL"})
    assert res is True
    assert mock_ws.send_json.called


def test_analytics_and_statistics():
    """Test NotificationAnalytics and NotificationStatistics."""
    analytics = NotificationAnalytics()
    analytics.record_created(priority="HIGH")
    analytics.record_delivered(duration_ms=10.0)
    analytics.record_read()

    stats = NotificationStatistics(analytics=analytics)
    summary = stats.summary()
    assert summary["notifications_created"] == 1
    assert summary["notifications_delivered"] == 1
    assert summary["notifications_read"] == 1


async def test_notification_engine_workflow():
    """Test NotificationEngine end-to-end event evaluation, creation, deduplication, and delivery."""
    conn_mgr = ConnectionManager()
    broadcaster = DashboardBroadcaster(manager=conn_mgr)

    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_json = AsyncMock()

    conn = WebSocketConnection(websocket=mock_ws, user_id="admin-123")
    await conn_mgr.connect(conn)
    conn_mgr.subscribe(conn.connection_id, "notifications")

    engine = NotificationEngine(
        connection_manager=conn_mgr,
        broadcaster=broadcaster,
    )
    engine.start()

    # 1. Manual notification creation
    notif = await engine.create_notification(
        title="High Memory Alert",
        message="RAM usage reached 92%",
        category="system",
        priority="HIGH",
    )
    await asyncio.sleep(0.05)
    assert notif["title"] == "High Memory Alert"
    assert mock_ws.send_json.called

    mock_ws.send_json.reset_mock()

    # 2. Duplicate notification -> raises DuplicateNotificationError
    with pytest.raises(DuplicateNotificationError):
        await engine.create_notification(
            title="High Memory Alert",
            message="RAM usage reached 92%",
            category="system",
            priority="HIGH",
        )

    # 3. Process event stream payload
    results = await engine.process_notification("mission.failed", {"mission_name": "Apollo"})
    assert len(results) == 1
    assert results[0]["title"] == "Mission Execution Failure"

    engine.stop()
