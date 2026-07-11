"""Execution context tracing an incoming AI Gateway request.
"""

from datetime import UTC, datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """Execution context for tracing an incoming AI Gateway request."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: Optional[uuid.UUID] = None
    session_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    provider: Optional[str] = None
    selected_model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
