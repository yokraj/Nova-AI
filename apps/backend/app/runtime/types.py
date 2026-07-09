"""Structured enums and types definitions for the Nova AI Runtime Kernel.

Defines state indicators for kernel engines, capability SDK adapters, and events.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class KernelState(str, Enum):
    """Execution state indicator for the core Runtime Kernel."""

    BOOTING = "booting"
    ONLINE = "online"
    MAINTENANCE = "maintenance"
    SHUTTING_DOWN = "shutting_down"
    OFFLINE = "offline"


class CapabilityState(str, Enum):
    """Lifecycle state indicator for registered Capabilities."""

    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    STOPPED = "stopped"


class RuntimeEvent(BaseModel):
    """Data container representing system events dispatched through the Event Bus."""

    topic: str = Field(
        ..., description="Topic namespace (e.g., 'system.boot', 'step.done')."
    )
    sender: str = Field(
        ..., description="The ID or name of the component that sent this event."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event dispatch timestamp (UTC).",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured key-value context payload dictionary.",
    )
    id: Optional[str] = Field(
        None, description="Optional unique identifier index."
    )
