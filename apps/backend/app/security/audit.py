"""Audit Event Models & DTOs Module.

Defines structured AuditEvent data models for security logging and compliance reporting.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Structured security audit event DTO."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: Optional[str] = Field(default=None, description="Target or executing user identifier")
    role: str = Field(default="anonymous", description="User identity role claim")
    ip_address: str = Field(default="127.0.0.1", description="Client IP address")
    endpoint: str = Field(default="/", description="Target API endpoint or WebSocket URI")
    action: str = Field(..., description="Action performed: login, read, write, connect, denied, etc.")
    resource: str = Field(..., description="Target system resource: dashboard, metrics, user, etc.")
    result: str = Field(default="success", description="Execution result status: success, failure, denied")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual event details")
