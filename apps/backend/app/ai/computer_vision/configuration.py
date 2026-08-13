"""Computer Vision configuration settings and schemas for Nova Universal Computer Understanding.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ComputerVisionConfiguration(BaseModel):
    """Configuration schema for Computer Vision & Adaptive GUI Intelligence runtime."""

    prefer_accessibility_apis: bool = Field(True, description="Prefer OS Accessibility & DOM APIs over OCR/vision")
    ocr_confidence_threshold: float = Field(0.65, description="Minimum confidence threshold for OCR text detection")
    multi_monitor_enabled: bool = Field(True, description="Enables multi-monitor screen capture and transformations")
    screen_memory_limit: int = Field(50, description="Maximum historical screens kept in memory")
    auto_recovery_enabled: bool = Field(True, description="Automatically attempt GUI recovery on automation failure")
    capture_resolution_max_width: int = Field(1920, description="Max capture width in pixels")
    capture_resolution_max_height: int = Field(1080, description="Max capture height in pixels")
    telemetry_enabled: bool = Field(True, description="Collect vision metrics and trace execution")
    cache_ttl_seconds: int = Field(1800, description="Cache expiration duration in seconds")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
