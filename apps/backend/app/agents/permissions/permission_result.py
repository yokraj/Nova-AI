"""PermissionResult schema defining authorization evaluation outputs.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.agents.base import AgentPermission


class PermissionResult(BaseModel):
    """Represents the response/outcome of a permission request evaluation."""

    granted: bool = Field(..., description="True if access is granted, False otherwise.")
    permission: AgentPermission = Field(..., description="The type of permission evaluated.")
    resource: str = Field(..., description="Target resource path or identifier.")
    reason: str = Field(..., description="Reasoning or description of decision outcome.")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for temporary permissions.")
