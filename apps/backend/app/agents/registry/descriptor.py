"""AgentDescriptor metadata configurations.
"""

from typing import List
import uuid
from pydantic import BaseModel, Field
from app.agents.base import AgentCapability, AgentPermission


class AgentDescriptor(BaseModel):
    """Descriptors detailing properties, capabilities, and access requirements of an agent."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique agent identifier.")
    name: str = Field(..., description="Unique human-readable identifier name.")
    version: str = Field("0.1.0", description="SemVer version.")
    description: str = Field(..., description="Details regarding agent function.")
    author: str = Field("Nova AI", description="Agent author or vendor.")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Capabilities supported.")
    permissions: List[AgentPermission] = Field(default_factory=list, description="Permissions allowed.")
    priority: int = Field(100, description="Priority priority coefficient.")
    enabled: bool = Field(True, description="True if allowed to initialize and run.")
    tags: List[str] = Field(default_factory=list, description="Classification tags for the agent.")

