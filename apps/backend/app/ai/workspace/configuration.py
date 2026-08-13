"""Configuration settings and schemas for Enterprise Workspace & Remote AI Orchestration Platform.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class WorkspaceConfiguration(BaseModel):
    """Configuration schema for Workspace platform."""

    default_workspace_type: str = Field("personal", description="Default workspace type: personal, developer, research, organization, education, enterprise")
    auto_sync_interval_sec: int = Field(300, description="Background delta synchronization interval in seconds")
    max_members_per_workspace: int = Field(1000, description="Maximum members limit per team or organization workspace")
    encryption_enabled: bool = Field(True, description="Enforce end-to-end TLS and payload encryption for remote agents")
    storage_dir: str = Field("./data/workspaces", description="Storage directory for workspace definitions and archives")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for workspace search and member presence")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom configuration settings")
