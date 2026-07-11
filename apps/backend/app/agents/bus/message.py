"""AgentEvent metadata models for pub-sub topics.
"""

from datetime import datetime, UTC
from typing import Any, Dict
import uuid
from pydantic import BaseModel, Field


class AgentEvent(BaseModel):
    """Represents an event published onto the communication bus."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique event identifier.")
    topic: str = Field(..., description="Event topic/routing key.")
    source: str = Field(..., description="Name or identifier of the source agent.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data content.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event occurrence timestamp.")
