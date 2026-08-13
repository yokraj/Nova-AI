"""Configuration settings and schemas for Universal Desktop, Browser & OS Automation Engine.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class DesktopAutomationConfiguration(BaseModel):
    """Configuration schema for Universal Desktop Automation Engine."""

    mouse_speed_multiplier: float = Field(1.0, description="Mouse cursor movement speed multiplier")
    verification_timeout_sec: float = Field(10.0, description="Default timeout in seconds for action verification")
    screenshot_quality: int = Field(85, description="JPEG/PNG screenshot compression quality percentage")
    auto_recovery_enabled: bool = Field(True, description="Automatically trigger visual and context recovery upon step failure")
    approval_required_for_destructive: bool = Field(True, description="Require human approval hold before executing destructive or sensitive actions")
    default_browser: str = Field("chrome", description="Default browser engine for web automation: chrome, edge, firefox, brave")
    storage_dir: str = Field("./data/desktop_automation", description="Directory for session states and execution history logs")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for GUI element detection and window maps")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional desktop automation configuration parameters")
