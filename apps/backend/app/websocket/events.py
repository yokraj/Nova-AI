"""WebSocket Event Router Module.

Maps domain event payload objects to target channel topics and creates formatted
WebSocketMessage JSON envelopes for broadcasting.
"""

from typing import Any, Dict, Tuple
import structlog

from app.websocket.schemas import WebSocketEventEnum, WebSocketMessage

logger = structlog.get_logger(__name__)

EVENT_CHANNEL_MAP: Dict[str, Tuple[str, str]] = {
    "SystemUpdated": ("system.updated", "system"),
    "ResourceUpdated": ("resource.updated", "resources"),
    "HealthUpdated": ("health.updated", "health"),
    "NotificationCreated": ("notification.created", "notifications"),
    "NotificationRead": ("notification.read", "notifications"),
    "MissionUpdated": ("mission.updated", "missions"),
    "AgentUpdated": ("agent.updated", "agents"),
    "AnalyticsUpdated": ("analytics.updated", "analytics"),
    "LogReceived": ("log.received", "logs"),
    "ConfigurationUpdated": ("configuration.updated", "configuration"),
    "DashboardSnapshotCreated": ("dashboard.snapshot.created", "dashboard"),
}


class EventRouter:
    """Routes domain event payloads to target streaming channel topics."""

    def route_event(self, event_name: str, payload: Dict[str, Any]) -> WebSocketMessage:
        """Converts event_name and payload dictionary into a typed WebSocketMessage DTO."""
        if event_name in EVENT_CHANNEL_MAP:
            event_type, channel = EVENT_CHANNEL_MAP[event_name]
        else:
            event_type = event_name.lower()
            channel = "dashboard"
            logger.debug("unmapped_event_routed_to_default_dashboard", event_name=event_name)

        return WebSocketMessage(
            event=event_type,
            channel=channel,
            payload=payload,
        )
