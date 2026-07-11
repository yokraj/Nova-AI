"""PermissionRequest schema defining inputs requested from agents.
"""

from datetime import datetime, UTC
import uuid
from pydantic import BaseModel, Field
from app.agents.base import AgentPermission


class PermissionRequest(BaseModel):
    """Represents a request from an agent to access a protected resource."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique permission request identifier.")
    agent_id: uuid.UUID = Field(..., description="Unique agent identifier requesting the permission.")
    permission: AgentPermission = Field(..., description="The type of permission being requested.")
    resource: str = Field(..., description="Specific target resource path or identifier.")
    reason: str = Field(..., description="Justification reason for requesting access.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Timestamp of the request.")
