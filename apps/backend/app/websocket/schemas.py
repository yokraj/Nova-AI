"""WebSocket Pydantic Schemas & DTO Envelopes Module.

Defines standardized JSON message models, client command frames,
and event topics for the Nova AI WebSocket Gateway.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class WebSocketEventEnum(str, Enum):
    """Supported WebSocket event type topics."""

    SYSTEM_UPDATED = "system.updated"
    RESOURCE_UPDATED = "resource.updated"
    HEALTH_UPDATED = "health.updated"
    NOTIFICATION_CREATED = "notification.created"
    NOTIFICATION_READ = "notification.read"
    MISSION_UPDATED = "mission.updated"
    AGENT_UPDATED = "agent.updated"
    ANALYTICS_UPDATED = "analytics.updated"
    LOG_RECEIVED = "log.received"
    CONFIGURATION_UPDATED = "configuration.updated"
    DASHBOARD_SNAPSHOT_CREATED = "dashboard.snapshot.created"
    HEARTBEAT_PING = "heartbeat.ping"
    HEARTBEAT_PONG = "heartbeat.pong"


class WebSocketMessage(BaseModel):
    """Standardized server-to-client JSON message envelope."""

    event: str = Field(..., description="Target event name identifier")
    channel: str = Field(..., description="Target subscription channel name")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )
    version: str = Field(default="1.0", description="Protocol format version")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured event payload data")


class WebSocketClientFrame(BaseModel):
    """Client-to-server incoming command frame schema."""

    action: str = Field(..., description="Command action: subscribe, unsubscribe, ping, pong, authenticate")
    channel: Optional[str] = Field(default=None, description="Target channel name for single channel action")
    channels: Optional[List[str]] = Field(default=None, description="List of target channel names for batch action")
    token: Optional[str] = Field(default=None, description="JWT bearer authentication token string")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional payload dictionary")


class WebSocketResponse(BaseModel):
    """Control response envelope returned to client after action execution."""

    status: str = Field(..., description="Action execution status: success, error")
    action: str = Field(..., description="Echoed input command action")
    message: str = Field(..., description="Status description or error message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata or subscription state")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )
