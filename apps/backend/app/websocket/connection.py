"""WebSocket Connection Wrapper Module.

Encapsulates individual client WebSocket socket state, identity claims,
RBAC permissions, channel subscriptions, and ping/pong timestamps.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set
import uuid
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
import structlog

from app.websocket.exceptions import ConnectionClosedError

logger = structlog.get_logger(__name__)


class WebSocketConnection:
    """Encapsulates active WebSocket client state and channel subscriptions."""

    def __init__(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        role: str = "user",
        permissions: Optional[Set[str]] = None,
        connection_id: Optional[uuid.UUID] = None,
    ) -> None:
        self.connection_id = connection_id or uuid.uuid4()
        self.websocket = websocket
        self.user_id = user_id
        self.role = role
        self.permissions = permissions or set()
        self.subscriptions: Set[str] = set()

        now = datetime.now(timezone.utc)
        self.connected_at = now
        self.last_ping = now
        self.last_pong = now

        logger.info("websocket_connection_created", connection_id=str(self.connection_id), user_id=user_id)

    @property
    def is_connected(self) -> bool:
        """Returns True if underlying socket is open."""
        return self.websocket.client_state == WebSocketState.CONNECTED

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Sends JSON payload data frame to client."""
        if not self.is_connected:
            raise ConnectionClosedError(str(self.connection_id))
        try:
            await self.websocket.send_json(data)
        except Exception as exc:
            logger.warning("websocket_send_failed", connection_id=str(self.connection_id), error=str(exc))
            raise ConnectionClosedError(str(self.connection_id)) from exc

    async def receive_json(self) -> Dict[str, Any]:
        """Receives JSON data frame from client."""
        if not self.is_connected:
            raise ConnectionClosedError(str(self.connection_id))
        try:
            return await self.websocket.receive_json()
        except Exception as exc:
            logger.warning("websocket_receive_failed", connection_id=str(self.connection_id), error=str(exc))
            raise ConnectionClosedError(str(self.connection_id)) from exc

    def subscribe(self, channel: str) -> None:
        """Subscribes connection to target channel topic."""
        self.subscriptions.add(channel)

    def unsubscribe(self, channel: str) -> None:
        """Unsubscribes connection from target channel topic."""
        self.subscriptions.discard(channel)

    def is_subscribed(self, channel: str) -> bool:
        """Checks if connection is subscribed to target channel topic."""
        return channel in self.subscriptions

    async def close(self, code: int = 1000, reason: Optional[str] = None) -> None:
        """Closes the underlying WebSocket socket connection."""
        if self.is_connected:
            try:
                await self.websocket.close(code=code, reason=reason)
                logger.info("websocket_closed", connection_id=str(self.connection_id), code=code, reason=reason)
            except Exception as exc:
                logger.debug("websocket_close_failed", connection_id=str(self.connection_id), error=str(exc))
