"""Asynchronous WebSocket Connection Manager Module.

Tracks active client connections, index mapping by channel topic and user identity,
and handles async broadcast distribution loops.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
import uuid
import structlog

from app.websocket.connection import WebSocketConnection
from app.websocket.exceptions import ChannelNotFoundError, ConnectionClosedError
from app.websocket.subscriptions import SUPPORTED_CHANNELS, SubscriptionManager

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Enterprise Asynchronous WebSocket Connection & Channel Manager."""

    def __init__(self) -> None:
        self._connections: Dict[uuid.UUID, WebSocketConnection] = {}
        self._channel_index: Dict[str, Set[uuid.UUID]] = {ch: set() for ch in SUPPORTED_CHANNELS}
        self.subscription_manager = SubscriptionManager(SUPPORTED_CHANNELS)

        logger.info("connection_manager_initialized")

    async def connect(self, connection: WebSocketConnection) -> None:
        """Registers an authenticated active connection."""
        self._connections[connection.connection_id] = connection
        logger.info(
            "connection_registered",
            connection_id=str(connection.connection_id),
            user_id=connection.user_id,
            active_total=len(self._connections),
        )

    async def disconnect(self, connection: WebSocketConnection) -> None:
        """Deregisters and cleans up an active connection."""
        cid = connection.connection_id
        if cid in self._connections:
            # Remove from channel index
            for channel in list(connection.subscriptions):
                if channel in self._channel_index:
                    self._channel_index[channel].discard(cid)

            # Close socket if open
            if connection.is_connected:
                await connection.close()

            del self._connections[cid]
            logger.info("connection_deregistered", connection_id=str(cid), active_total=len(self._connections))

    async def disconnect_all(self) -> None:
        """Closes and disconnects all active client connections."""
        connections = list(self._connections.values())
        for conn in connections:
            await self.disconnect(conn)

    def is_connected(self, connection_id: uuid.UUID) -> bool:
        """Returns True if connection ID exists and socket is connected."""
        conn = self._connections.get(connection_id)
        return conn is not None and conn.is_connected

    def connection_count(self) -> int:
        """Returns count of active connected clients."""
        return len(self._connections)

    def get_connection(self, connection_id: uuid.UUID) -> Optional[WebSocketConnection]:
        """Returns connection instance by UUID."""
        return self._connections.get(connection_id)

    def list_connections(self) -> List[WebSocketConnection]:
        """Returns list of active connection instances."""
        return list(self._connections.values())

    def register_channel(self, channel: str) -> None:
        """Registers a new streaming channel topic dynamically."""
        if channel not in self._channel_index:
            self._channel_index[channel] = set()
            self.subscription_manager.valid_channels.add(channel)
            logger.info("channel_registered", channel=channel)

    def unregister_channel(self, channel: str) -> None:
        """Unregisters a streaming channel topic dynamically."""
        if channel in self._channel_index:
            del self._channel_index[channel]
            self.subscription_manager.valid_channels.discard(channel)
            logger.info("channel_unregistered", channel=channel)

    def subscribe(self, connection_id: uuid.UUID, channel: str) -> bool:
        """Subscribes connection ID to target channel topic."""
        conn = self.get_connection(connection_id)
        if not conn:
            raise ConnectionClosedError(str(connection_id))

        success = self.subscription_manager.subscribe(conn, channel)
        if success:
            if channel not in self._channel_index:
                self._channel_index[channel] = set()
            self._channel_index[channel].add(connection_id)
        return success

    def unsubscribe(self, connection_id: uuid.UUID, channel: str) -> bool:
        """Unsubscribes connection ID from target channel topic."""
        conn = self.get_connection(connection_id)
        if not conn:
            return False

        success = self.subscription_manager.unsubscribe(conn, channel)
        if success and channel in self._channel_index:
            self._channel_index[channel].discard(connection_id)
        return success

    def list_subscriptions(self, connection_id: uuid.UUID) -> List[str]:
        """Returns subscriptions for connection ID."""
        conn = self.get_connection(connection_id)
        if not conn:
            return []
        return self.subscription_manager.list_user_subscriptions(conn)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcasts payload to ALL active client connections."""
        active = list(self._connections.values())
        if not active:
            return

        tasks = [conn.send_json(message) for conn in active if conn.is_connected]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for conn, res in zip(active, results):
            if isinstance(res, Exception):
                logger.warning("broadcast_item_failed", connection_id=str(conn.connection_id), error=str(res))

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]) -> None:
        """Broadcasts payload to clients subscribed to target channel topic."""
        subscribers_ids = list(self._channel_index.get(channel, set()))
        if not subscribers_ids:
            return

        subscribers = [self._connections[cid] for cid in subscribers_ids if cid in self._connections]
        tasks = [conn.send_json(message) for conn in subscribers if conn.is_connected]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for conn, res in zip(subscribers, results):
            if isinstance(res, Exception):
                logger.warning("channel_broadcast_item_failed", channel=channel, connection_id=str(conn.connection_id), error=str(res))

    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """Broadcasts payload to all active connections belonging to user_id."""
        user_conns = [conn for conn in self._connections.values() if conn.user_id == str(user_id) and conn.is_connected]
        if not user_conns:
            return

        tasks = [conn.send_json(message) for conn in user_conns]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_except(self, exclude_connection_id: uuid.UUID, channel: str, message: Dict[str, Any]) -> None:
        """Broadcasts payload to channel subscribers excluding specific connection ID."""
        subscribers_ids = [cid for cid in self._channel_index.get(channel, set()) if cid != exclude_connection_id]
        if not subscribers_ids:
            return

        subscribers = [self._connections[cid] for cid in subscribers_ids if cid in self._connections]
        tasks = [conn.send_json(message) for conn in subscribers if conn.is_connected]
        await asyncio.gather(*tasks, return_exceptions=True)
