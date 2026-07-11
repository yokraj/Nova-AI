"""AgentRequest model tracking context execution query parameters.
"""

from datetime import datetime, UTC
from typing import Any, Dict
import uuid
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Represents a request sent from one agent to another."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique request identifier.")
    sender: str = Field(..., description="Name or identifier of the sender agent.")
    receiver: str = Field(..., description="Name or identifier of the receiver agent.")
    conversation_id: uuid.UUID = Field(..., description="Conversation/session identifier.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Request payload parameters.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp.")
