"""Configuration settings and schemas for Universal Workflow Learning & No-Code Automation Studio.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class WorkflowStudioConfiguration(BaseModel):
    """Configuration schema for Workflow Studio platform."""

    auto_extract_variables: bool = Field(True, description="Automatically detect and extract variables like emails, OTPs, amounts")
    default_timeout_sec: float = Field(30.0, description="Default timeout in seconds per workflow action step")
    max_recording_duration_sec: float = Field(3600.0, description="Maximum recording duration limit in seconds")
    encryption_enabled: bool = Field(True, description="Encrypt sensitive variables like passwords and secret keys")
    storage_dir: str = Field("./data/workflows", description="Storage directory for workflow definitions")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for workflow templates and definitions")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom configuration settings")
