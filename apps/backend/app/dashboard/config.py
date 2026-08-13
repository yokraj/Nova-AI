"""Dashboard Configuration Module.

Provides configuration management structures for the Enterprise Dashboard,
defining interval rates, memory limits, and socket parameters.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DashboardConfig(BaseModel):
    """Enterprise Dashboard Configuration settings placeholder class.
    
    Attributes:
        refresh_interval: Interval in seconds between dashboard UI state syncs.
        cache_ttl: Time-to-live in seconds for cached dashboard telemetry.
        metrics_interval: Interval in seconds for sampling system/node metrics.
        heartbeat_interval: WebSocket ping-pong keepalive interval in seconds.
        max_connections: Maximum permitted concurrent WebSocket sessions.
        max_notifications: Maximum notification event log buffer capacity.
        max_event_history: Maximum size of historical event memory buffer.
    """

    refresh_interval: int = Field(
        default=5, description="Dashboard telemetry refresh interval (seconds)"
    )
    cache_ttl: int = Field(
        default=60, description="Dashboard cache time-to-live (seconds)"
    )
    metrics_interval: int = Field(
        default=10, description="System metrics sampling interval (seconds)"
    )
    heartbeat_interval: int = Field(
        default=15, description="WebSocket heartbeat keepalive interval (seconds)"
    )
    max_connections: int = Field(
        default=1000, description="Maximum concurrent dashboard WebSocket client connections"
    )
    max_notifications: int = Field(
        default=500, description="Maximum notifications retained in buffer memory"
    )
    max_event_history: int = Field(
        default=10000, description="Maximum dashboard event history buffer capacity"
    )
