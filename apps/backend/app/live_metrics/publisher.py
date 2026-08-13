"""Metrics Publisher Module.

Delegates telemetry payload broadcasting to the existing DashboardBroadcaster
from M3.4.22.6, ensuring consistent JSON message envelopes across channels.
"""

from typing import Any, Dict, Optional
import structlog

from app.websocket.broadcaster import DashboardBroadcaster

logger = structlog.get_logger(__name__)


class MetricsPublisher:
    """Delegates real-time channel broadcasting to DashboardBroadcaster."""

    def __init__(self, broadcaster: DashboardBroadcaster) -> None:
        self.broadcaster = broadcaster
        logger.info("metrics_publisher_initialized")

    async def publish_dashboard(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_dashboard(payload)

    async def publish_resources(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_resources(payload)

    async def publish_cpu(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_cpu(payload)

    async def publish_memory(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_memory(payload)

    async def publish_disk(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_disk(payload)

    async def publish_network(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_network(payload)

    async def publish_gpu(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_gpu(payload)

    async def publish_processes(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_processes(payload)

    async def publish_system(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_system(payload)

    async def publish_health(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_health(payload)

    async def publish_notifications(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_notifications(payload)

    async def publish_events(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_events(payload)

    async def publish_agents(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_agents(payload)

    async def publish_missions(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_missions(payload)

    async def publish_logs(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_logs(payload)

    async def publish_analytics(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_analytics(payload) if hasattr(self.broadcaster, "broadcast_analytics") else await self.broadcaster._send_to_channel("analytics.updated", "analytics", payload)

    async def publish_configuration(self, payload: Dict[str, Any]) -> None:
        await self.broadcaster.broadcast_configuration(payload)
