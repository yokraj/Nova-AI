"""Configuration settings profiles for the Human Approval & Safety Engine.
"""

from pydantic_settings import BaseSettings
from pydantic import Field

class SafetyConfiguration(BaseSettings):
    """Configuration settings for risk classification, queue timeouts, and audit logs."""

    approval_timeout_seconds: int = Field(default=3600, description="Expiration duration in seconds for pending approvals (1 hour)")
    enable_strict_mode: bool = Field(default=True, description="Enforces safety validation checks on all action executions")
    storage_path: str = Field(default="./data/safety", description="Local directory path to save serialized audit records")

    class Config:
        env_prefix = "NOVA_SAFETY_"
        case_sensitive = False
