"""Configuration settings for the Enterprise AI Gateway.
"""

from typing import Optional
from pydantic import BaseModel, Field


class GatewayConfig(BaseModel):
    """Configuration settings for the Enterprise AI Gateway."""

    default_model: str = Field("gpt-4o", description="Fallback model when none specified.")
    timeout_seconds: float = Field(30.0, description="Default timeout limit in seconds.")
    max_retries: int = Field(3, description="Default max execution retries limit.")
    backoff_factor: float = Field(1.5, description="Backoff scale multiplier.")
