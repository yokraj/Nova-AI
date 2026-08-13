"""Nova AI Enterprise WebSocket Gateway Package.

Provides authenticated, scalable, real-time bi-directional streaming for Nova AI,
handling connection lifecycle, JWT authorization claims, channel subscriptions,
ping/pong heartbeats, and event broadcasting.
"""

from app.websocket.authentication import authenticate_websocket_connection
from app.websocket.broadcaster import DashboardBroadcaster
from app.websocket.connection import WebSocketConnection
from app.websocket.events import EventRouter
from app.websocket.exceptions import (
    BroadcastError,
    ChannelNotFoundError,
    ConnectionClosedError,
    HeartbeatTimeoutError,
    SubscriptionError,
    WebSocketAuthenticationError,
    WebSocketGatewayError,
)
from app.websocket.heartbeat import HeartbeatManager
from app.websocket.manager import ConnectionManager
from app.websocket.router import manager, router
from app.websocket.schemas import WebSocketClientFrame, WebSocketMessage, WebSocketResponse
from app.websocket.subscriptions import SubscriptionManager

__all__ = [
    "ConnectionManager",
    "DashboardBroadcaster",
    "HeartbeatManager",
    "EventRouter",
    "SubscriptionManager",
    "WebSocketConnection",
    "authenticate_websocket_connection",
    "router",
    "manager",
    "WebSocketMessage",
    "WebSocketClientFrame",
    "WebSocketResponse",
    "WebSocketGatewayError",
    "WebSocketAuthenticationError",
    "SubscriptionError",
    "ChannelNotFoundError",
    "ConnectionClosedError",
    "HeartbeatTimeoutError",
    "BroadcastError",
]
