"""SystemEvent schema defining distributed runtime telemetry payloads.
"""

from datetime import datetime, UTC
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field
from app.runtime.events.topics import Topic


class SystemEvent(BaseModel):
    """Represents a system-wide event distributed across the application runtime."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique system event identifier.")
    topic: Topic = Field(..., description="The category/topic of this system event.")
    source: str = Field(..., description="Origin source system/component publishing the event.")
    correlation_id: Optional[uuid.UUID] = Field(None, description="Identifier linking related causal transactions.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event metadata parameters payload.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Occurrence timestamp of the event.")
