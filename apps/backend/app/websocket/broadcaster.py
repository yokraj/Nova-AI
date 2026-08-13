"""Dashboard Broadcaster Module.

Provides typed async helper methods for serializing and broadcasting JSON event payloads
across all dashboard channel topics via ConnectionManager.
"""

from typing import Any, Dict, Optional
import structlog

from app.websocket.events import EventRouter
from app.websocket.manager import ConnectionManager
from app.websocket.schemas import WebSocketMessage

logger = structlog.get_logger(__name__)


class DashboardBroadcaster:
    """Enterprise Dashboard Broadcaster dispatching real-time WebSocket payloads."""

    def __init__(self, manager: ConnectionManager, event_router: Optional[EventRouter] = None) -> None:
        self.manager = manager
        self.event_router = event_router or EventRouter()
        logger.info("dashboard_broadcaster_initialized")

    async def _send_to_channel(self, event_name: str, channel: str, payload: Dict[str, Any]) -> None:
        """Constructs WebSocketMessage envelope and broadcasts to target channel subscribers."""
        msg = WebSocketMessage(
            event=event_name,
            channel=channel,
            payload=payload,
        )
        logger.info("broadcasting_event", event_type=event_name, channel=channel)
        await self.manager.broadcast_to_channel(channel, msg.model_dump())

    async def broadcast_dashboard(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("dashboard.snapshot.created", "dashboard", payload)

    async def broadcast_system(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("system.updated", "system", payload)

    async def broadcast_resources(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("resource.updated", "resources", payload)

    async def broadcast_cpu(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("cpu.updated", "cpu", payload)

    async def broadcast_memory(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("memory.updated", "memory", payload)

    async def broadcast_disk(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("disk.updated", "disk", payload)

    async def broadcast_network(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("network.updated", "network", payload)

    async def broadcast_gpu(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("gpu.updated", "gpu", payload)

    async def broadcast_processes(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("process.updated", "processes", payload)

    async def broadcast_notifications(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("notification.created", "notifications", payload)

    async def broadcast_events(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("event.created", "events", payload)

    async def broadcast_health(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("health.updated", "health", payload)

    async def broadcast_agents(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("agent.updated", "agents", payload)

    async def broadcast_missions(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("mission.updated", "missions", payload)

    async def broadcast_logs(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("log.received", "logs", payload)

    async def broadcast_voice(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("voice.updated", "voice", payload)

    async def broadcast_models(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("model.updated", "models", payload)

    async def broadcast_workflows(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("workflow.updated", "workflows", payload)

    async def broadcast_configuration(self, payload: Dict[str, Any]) -> None:
        await self._send_to_channel("configuration.updated", "configuration", payload)
