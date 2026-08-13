"""Configuration settings and schemas for Universal Skills Marketplace & SDK.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class SkillConfiguration(BaseModel):
    """Configuration schema for Skills Marketplace and SDK platform."""

    skills_directory: str = Field("./data/skills", description="Directory path for installed skill packages")
    auto_update_enabled: bool = Field(True, description="Enable automatic background skill update checks")
    auto_enable_new_skills: bool = Field(True, description="Automatically enable newly installed skills")
    permission_prompt_policy: str = Field("STRICT", description="Policy for sensitive permissions ('STRICT', 'PROMPT', 'ALLOW')")
    sandbox_execution: bool = Field(True, description="Run skills in isolated execution sandbox")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for marketplace search results")
    telemetry_enabled: bool = Field(True, description="Collect usage metrics and execution statistics")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom configuration settings")
