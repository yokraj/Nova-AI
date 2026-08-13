"""WebSocket Router Module.

Exposes the /ws/dashboard production WebSocket endpoint for real-time bi-directional
dashboard event streaming, channel subscriptions, and ping/pong heartbeats.
"""

from typing import Any, Dict, Optional
import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.websocket.authentication import authenticate_websocket_connection
from app.websocket.connection import WebSocketConnection
from app.websocket.exceptions import (
    ChannelNotFoundError,
    ConnectionClosedError,
    WebSocketAuthenticationError,
)
from app.websocket.manager import ConnectionManager
from app.websocket.schemas import WebSocketClientFrame, WebSocketResponse

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["WebSocket Gateway"])

# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None, description="JWT Bearer Authentication Token"),
) -> None:
    """Production WebSocket gateway endpoint for real-time dashboard telemetry streaming."""
    # 1. Authenticate Handshake
    try:
        auth_data = authenticate_websocket_connection(websocket, token)
    except WebSocketAuthenticationError as exc:
        logger.warning("websocket_handshake_auth_failed", error=str(exc))
        # Reject unauthenticated connection
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return
    except Exception as exc:
        logger.error("websocket_handshake_unexpected_error", error=str(exc))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Handshake error")
        return

    # 2. Check RBAC permissions
    permissions = auth_data.get("permissions", set())
    if "dashboard:read" not in permissions and "dashboard:overview:read" not in permissions:
        logger.warning("websocket_handshake_forbidden", user_id=auth_data.get("user_id"))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Insufficient permissions")
        return

    # 3. Accept Handshake Connection
    await websocket.accept()

    connection = WebSocketConnection(
        websocket=websocket,
        user_id=auth_data.get("user_id"),
        role=auth_data.get("role", "user"),
        permissions=permissions,
    )

    await manager.connect(connection)

    # Auto-subscribe to default 'dashboard' channel topic
    manager.subscribe(connection.connection_id, "dashboard")

    # Send Connection Handshake Acknowledgement Frame
    ack_response = WebSocketResponse(
        status="success",
        action="authenticate",
        message="WebSocket connection established successfully.",
        data={
            "connection_id": str(connection.connection_id),
            "user_id": connection.user_id,
            "subscriptions": manager.list_subscriptions(connection.connection_id),
        },
    )
    await connection.send_json(ack_response.model_dump())

    # 4. Message Loop
    try:
        while True:
            raw_data = await connection.receive_json()
            try:
                frame = WebSocketClientFrame(**raw_data)
                action = frame.action.lower()

                if action == "ping":
                    connection.last_pong = connection.connected_at
                    pong_res = WebSocketResponse(
                        status="success",
                        action="pong",
                        message="Heartbeat pong response",
                    )
                    await connection.send_json(pong_res.model_dump())

                elif action == "pong":
                    connection.last_pong = connection.connected_at

                elif action == "subscribe":
                    target_channels = frame.channels or ([frame.channel] if frame.channel else [])
                    subscribed = manager.subscription_manager.subscribe_many(connection, target_channels)
                    for ch in subscribed:
                        manager.register_channel(ch)
                        if ch not in manager._channel_index:
                            manager._channel_index[ch] = set()
                        manager._channel_index[ch].add(connection.connection_id)

                    res = WebSocketResponse(
                        status="success",
                        action="subscribe",
                        message=f"Subscribed to {len(subscribed)} channels.",
                        data={"subscribed": subscribed, "active": manager.list_subscriptions(connection.connection_id)},
                    )
                    await connection.send_json(res.model_dump())

                elif action == "unsubscribe":
                    target_channels = frame.channels or ([frame.channel] if frame.channel else [])
                    unsubscribed = manager.subscription_manager.unsubscribe_many(connection, target_channels)
                    for ch in unsubscribed:
                        if ch in manager._channel_index:
                            manager._channel_index[ch].discard(connection.connection_id)

                    res = WebSocketResponse(
                        status="success",
                        action="unsubscribe",
                        message=f"Unsubscribed from {len(unsubscribed)} channels.",
                        data={"unsubscribed": unsubscribed, "active": manager.list_subscriptions(connection.connection_id)},
                    )
                    await connection.send_json(res.model_dump())

                else:
                    err_res = WebSocketResponse(
                        status="error",
                        action=action,
                        message=f"Unknown or unsupported command action '{action}'.",
                    )
                    await connection.send_json(err_res.model_dump())

            except (ChannelNotFoundError, ConnectionClosedError) as exc:
                err_res = WebSocketResponse(
                    status="error",
                    action=raw_data.get("action", "unknown"),
                    message=str(exc),
                )
                await connection.send_json(err_res.model_dump())
            except Exception as exc:
                logger.warning("websocket_frame_parse_failed", error=str(exc))
                err_res = WebSocketResponse(
                    status="error",
                    action=raw_data.get("action", "unknown"),
                    message=f"Malformed frame payload: {str(exc)}",
                )
                await connection.send_json(err_res.model_dump())

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", connection_id=str(connection.connection_id))
    except Exception as exc:
        logger.warning("websocket_session_loop_terminated", connection_id=str(connection.connection_id), error=str(exc))
    finally:
        await manager.disconnect(connection)
