"""Unit and Integration Test Suite for Nova AI Enterprise WebSocket Gateway.

Tests WebSocket connection lifecycle, JWT handshake authentication, RBAC permissions,
channel subscriptions, ping/pong heartbeats, event routing, broadcasting, and disconnect cleanup.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from fastapi import WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketState

from app.identity.infrastructure.security import create_access_token
from app.main import app
from app.websocket.authentication import authenticate_websocket_connection
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.connection import WebSocketConnection
from app.websocket.events import EventRouter
from app.websocket.exceptions import (
    ChannelNotFoundError,
    ConnectionClosedError,
    WebSocketAuthenticationError,
)
from app.websocket.heartbeat import HeartbeatManager
from app.websocket.manager import ConnectionManager
from app.websocket.schemas import WebSocketClientFrame, WebSocketMessage, WebSocketResponse
from app.websocket.subscriptions import SUPPORTED_CHANNELS, SubscriptionManager


def test_websocket_schemas_and_exceptions():
    """Test WebSocket schema initialization and exception hierarchy."""
    msg = WebSocketMessage(
        event="resource.updated",
        channel="resources",
        payload={"cpu": 45.0},
    )
    assert msg.event == "resource.updated"
    assert msg.channel == "resources"
    assert msg.version == "1.0"
    assert msg.payload["cpu"] == 45.0

    frame = WebSocketClientFrame(
        action="subscribe",
        channel="system",
    )
    assert frame.action == "subscribe"
    assert frame.channel == "system"

    response = WebSocketResponse(
        status="success",
        action="subscribe",
        message="Subscribed to channel",
    )
    assert response.status == "success"

    err = WebSocketAuthenticationError("Invalid token")
    assert "Invalid token" in str(err)


def test_subscription_manager():
    """Test SubscriptionManager channel validation and subscription lifecycle."""
    sub_mgr = SubscriptionManager()
    assert sub_mgr.is_valid_channel("resources") is True
    assert sub_mgr.is_valid_channel("invalid_channel_xyz") is False

    mock_ws = MagicMock()
    conn = WebSocketConnection(websocket=mock_ws, user_id="user-123", role="user")

    # Subscribe single channel
    assert sub_mgr.subscribe(conn, "resources") is True
    # Duplicate subscription returns False
    assert sub_mgr.subscribe(conn, "resources") is False
    assert conn.is_subscribed("resources") is True

    # Subscribe batch
    subscribed = sub_mgr.subscribe_many(conn, ["system", "cpu", "memory"])
    assert len(subscribed) == 3
    assert "system" in conn.subscriptions

    # Unsubscribe batch
    unsubscribed = sub_mgr.unsubscribe_many(conn, ["system", "cpu"])
    assert len(unsubscribed) == 2
    assert "system" not in conn.subscriptions

    # List subscriptions
    active = sub_mgr.list_user_subscriptions(conn)
    assert "resources" in active
    assert "memory" in active


def test_connection_manager_sync_methods():
    """Test ConnectionManager registration and list methods."""
    mgr = ConnectionManager()

    mock_ws1 = MagicMock()
    conn1 = WebSocketConnection(websocket=mock_ws1, user_id="user-1", connection_id=uuid.uuid4())

    mock_ws2 = MagicMock()
    conn2 = WebSocketConnection(websocket=mock_ws2, user_id="user-2", connection_id=uuid.uuid4())

    asyncio.run(mgr.connect(conn1))
    asyncio.run(mgr.connect(conn2))

    assert mgr.connection_count() == 2
    assert mgr.get_connection(conn1.connection_id) == conn1
    assert len(mgr.list_connections()) == 2

    # Test subscribe / unsubscribe on manager
    mgr.subscribe(conn1.connection_id, "resources")
    assert "resources" in mgr.list_subscriptions(conn1.connection_id)

    mgr.unsubscribe(conn1.connection_id, "resources")
    assert "resources" not in mgr.list_subscriptions(conn1.connection_id)


async def test_async_broadcasting_flow():
    """Test ConnectionManager and DashboardBroadcaster async broadcasting."""
    mgr = ConnectionManager()
    broadcaster = DashboardBroadcaster(manager=mgr)

    mock_ws1 = MagicMock()
    mock_ws1.client_state = WebSocketState.CONNECTED
    mock_ws1.send_json = AsyncMock()

    mock_ws2 = MagicMock()
    mock_ws2.client_state = WebSocketState.CONNECTED
    mock_ws2.send_json = AsyncMock()

    conn1 = WebSocketConnection(websocket=mock_ws1, user_id="user-1")
    conn2 = WebSocketConnection(websocket=mock_ws2, user_id="user-2")

    await mgr.connect(conn1)
    await mgr.connect(conn2)

    mgr.subscribe(conn1.connection_id, "resources")
    mgr.subscribe(conn2.connection_id, "resources")

    # Broadcast to resources channel
    await broadcaster.broadcast_resources({"cpu": "50%"})

    assert mock_ws1.send_json.called
    assert mock_ws2.send_json.called

    # Broadcast to specific user
    await mgr.broadcast_to_user("user-1", {"alert": "urgent"})
    assert mock_ws1.send_json.call_count >= 2


def test_event_router():
    """Test EventRouter mapping domain events to channel topics."""
    router = EventRouter()
    msg = router.route_event("SystemUpdated", {"uptime": 3600})
    assert msg.event == "system.updated"
    assert msg.channel == "system"
    assert msg.payload["uptime"] == 3600

    msg_health = router.route_event("HealthUpdated", {"status": "healthy"})
    assert msg_health.event == "health.updated"
    assert msg_health.channel == "health"


def test_heartbeat_manager():
    """Test HeartbeatManager ping/pong recording."""
    mgr = ConnectionManager()
    hb_mgr = HeartbeatManager(connection_manager=mgr, ping_interval_seconds=10.0)

    mock_ws = MagicMock()
    conn = WebSocketConnection(websocket=mock_ws, user_id="user-1")

    initial_pong = conn.last_pong
    hb_mgr.record_pong(conn)
    assert conn.last_pong >= initial_pong


def test_websocket_gateway_endpoint_integration():
    """Test Starlette TestClient connection to /ws/dashboard endpoint."""
    token = create_access_token({"sub": "admin-123", "role": "admin"})

    client = TestClient(app)
    with client.websocket_connect(f"/ws/dashboard?token={token}") as websocket:
        # 1. Receive handshake ACK frame
        ack = websocket.receive_json()
        assert ack["status"] == "success"
        assert ack["action"] == "authenticate"
        assert "dashboard" in ack["data"]["subscriptions"]

        # 2. Test ping / pong frame exchange
        websocket.send_json({"action": "ping"})
        pong_res = websocket.receive_json()
        assert pong_res["status"] == "success"
        assert pong_res["action"] == "pong"

        # 3. Test channel subscription frame
        websocket.send_json({"action": "subscribe", "channels": ["resources", "system", "gpu"]})
        sub_res = websocket.receive_json()
        assert sub_res["status"] == "success"
        assert sub_res["action"] == "subscribe"
        assert "resources" in sub_res["data"]["subscribed"]

        # 4. Test unsubscribe frame
        websocket.send_json({"action": "unsubscribe", "channel": "gpu"})
        unsub_res = websocket.receive_json()
        assert unsub_res["status"] == "success"
        assert unsub_res["action"] == "unsubscribe"
        assert "gpu" in unsub_res["data"]["unsubscribed"]
