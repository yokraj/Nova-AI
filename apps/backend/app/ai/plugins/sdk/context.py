"""Execution context object provided to plugins during capability invocation."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PluginContext(BaseModel):
    """Runtime context injected into plugin capability execution."""

    agent_id: str = "system"
    mission_id: Optional[str] = None
    workspace_path: str = "./"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    granted_permissions: list = Field(default_factory=list)
