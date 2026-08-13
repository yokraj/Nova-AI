"""Copilot configuration settings and schemas for Nova AI Software Copilot.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class CopilotConfiguration(BaseModel):
    """Configuration schema for AI Software Copilot execution runtime."""

    default_language: str = Field("python", description="Default primary programming language")
    default_architecture: str = Field("modular_monolith", description="Default architectural pattern")
    local_first: bool = Field(True, description="Enables local-first execution and model preferences")
    voice_updates_enabled: bool = Field(True, description="Enables voice progress reporting")
    auto_generate_tests: bool = Field(True, description="Automatically generates test suite during code generation")
    auto_git_commit: bool = Field(True, description="Automatically creates git commits for major SDLC milestones")
    max_code_files_per_generation: int = Field(50, description="Maximum files generated per task")
    telemetry_enabled: bool = Field(True, description="Collect copilot metrics and trace execution")
    cache_ttl_seconds: int = Field(3600, description="Cache expiration duration in seconds")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
