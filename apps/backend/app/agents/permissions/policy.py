"""PermissionPolicy configuration schemas.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from app.agents.base import AgentPermission
from app.agents.permissions.resource import ResourceType


class PolicyEffect(str, Enum):
    """Action effects for permission policies."""

    ALLOW = "allow"
    DENY = "deny"
    PROMPT_USER = "prompt_user"


class PolicyDuration(str, Enum):
    """Duration modes for permission grants."""

    TEMPORARY = "temporary"
    PERMANENT = "permanent"


class PermissionPolicy(BaseModel):
    """Represents a security policy governing agent access rights to protected resources."""

    policy_id: str = Field(..., description="Unique policy identifier.")
    agent_id: Optional[str] = Field(None, description="Optional target agent ID, or '*' for all agents.")
    permission: AgentPermission = Field(..., description="The target permission category.")
    resource_type: ResourceType = Field(..., description="The target system resource type.")
    resource_pattern: str = Field("*", description="Glob pattern matching specific resource paths.")
    effect: PolicyEffect = Field(PolicyEffect.ALLOW, description="Policy evaluation effect.")
    duration: PolicyDuration = Field(PolicyDuration.PERMANENT, description="Duration type of the grant/policy.")
    ttl_seconds: Optional[int] = Field(None, description="TTL in seconds if duration is temporary.")
