"""WebSocket Heartbeat & Idle Timeout Manager Module.

Monitors active WebSocket ping/pong frame exchanges, detects heartbeat timeouts,
and cleans up stale or idle connections automatically.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional
import structlog

from app.websocket.connection import WebSocketConnection
from app.websocket.manager import ConnectionManager
from app.websocket.schemas import WebSocketMessage

logger = structlog.get_logger(__name__)


class HeartbeatManager:
    """Monitors ping/pong heartbeat health and cleans up stale client sockets."""

    def __init__(
        self,
        connection_manager: ConnectionManager,
        ping_interval_seconds: float = 30.0,
        timeout_seconds: float = 60.0,
        idle_timeout_seconds: float = 300.0,
    ) -> None:
        self.manager = connection_manager
        self.ping_interval = ping_interval_seconds
        self.timeout = timeout_seconds
        self.idle_timeout = idle_timeout_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

        logger.info(
            "heartbeat_manager_initialized",
            ping_interval=self.ping_interval,
            timeout=self.timeout,
            idle_timeout=self.idle_timeout,
        )

    def record_ping(self, connection: WebSocketConnection) -> None:
        """Updates last_ping timestamp for connection."""
        connection.last_ping = datetime.now(timezone.utc)

    def record_pong(self, connection: WebSocketConnection) -> None:
        """Updates last_pong timestamp for connection."""
        connection.last_pong = datetime.now(timezone.utc)
        logger.debug("heartbeat_pong_received", connection_id=str(connection.connection_id))

    async def check_heartbeats(self) -> None:
        """Checks ping/pong ages across all active connections and disconnects stale clients."""
        now = datetime.now(timezone.utc)
        connections = self.manager.list_connections()

        for conn in connections:
            if not conn.is_connected:
                continue

            pong_age = (now - conn.last_pong).total_seconds()
            ping_age = (now - conn.last_ping).total_seconds()

            # 1. Send Ping Frame if ping interval exceeded
            if ping_age >= self.ping_interval:
                try:
                    self.record_ping(conn)
                    msg = WebSocketMessage(
                        event="heartbeat.ping",
                        channel="system",
                        payload={"connection_id": str(conn.connection_id)},
                    )
                    await conn.send_json(msg.model_dump())
                except Exception as exc:
                    logger.warning("heartbeat_ping_send_failed", connection_id=str(conn.connection_id), error=str(exc))

            # 2. Timeout check: if no pong response within timeout_seconds
            if pong_age > self.timeout:
                logger.warning(
                    "heartbeat_timeout_disconnecting",
                    connection_id=str(conn.connection_id),
                    pong_age=pong_age,
                    timeout=self.timeout,
                )
                await self.manager.disconnect(conn)

    async def _heartbeat_loop(self) -> None:
        """Periodic background heartbeat monitoring loop."""
        while self._running:
            try:
                await self.check_heartbeats()
            except Exception as exc:
                logger.error("heartbeat_loop_error", error=str(exc))
            await asyncio.sleep(self.ping_interval)

    def start(self) -> None:
        """Starts the background heartbeat monitoring loop."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._heartbeat_loop())
            logger.info("heartbeat_manager_started")

    def stop(self) -> None:
        """Stops the background heartbeat monitoring loop."""
        if self._running:
            self._running = False
            if self._task and not self._task.done():
                self._task.cancel()
            logger.info("heartbeat_manager_stopped")
