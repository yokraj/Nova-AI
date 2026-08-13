"""Kernel configuration settings and schemas for Nova AI Operating System.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class KernelConfiguration(BaseModel):
    """Configuration schema for AI OS Kernel execution runtime."""

    operating_mode: str = Field("VOICE", description="Default operating mode (VOICE, TEXT, SILENT, AUTONOMOUS, ASSISTED, DEBUG, COPILOT)")
    priority_level: str = Field("NORMAL", description="Default priority level (CRITICAL, HIGH, NORMAL, LOW, BACKGROUND)")
    voice_first_enabled: bool = Field(True, description="Enables voice-first interaction pipeline")
    auto_verification: bool = Field(True, description="Enables post-execution verification checks")
    security_approval_required: bool = Field(True, description="Requires user approval for sensitive actions")
    max_concurrent_tasks: int = Field(10, description="Maximum concurrent task limit in dynamic execution DAG")
    max_retry_attempts: int = Field(3, description="Maximum automated recovery retry count")
    cpu_warning_threshold: float = Field(85.0, description="CPU usage percent warning threshold")
    ram_warning_threshold: float = Field(85.0, description="RAM usage percent warning threshold")
    telemetry_enabled: bool = Field(True, description="Collect kernel metrics and event traces")
    cache_ttl_seconds: int = Field(3600, description="Cache expiration duration in seconds")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
