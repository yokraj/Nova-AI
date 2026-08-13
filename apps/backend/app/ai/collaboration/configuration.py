"""Configuration settings profiles for the Collaboration Engine.
"""

from pydantic_settings import BaseSettings
from pydantic import Field

class CollaborationConfiguration(BaseSettings):
    """Configuration settings for local agent collaborations."""

    negotiation_timeout_ms: int = Field(default=5000, description="Max milliseconds for negotiation bidding rounds")
    consensus_timeout_ms: int = Field(default=8000, description="Max milliseconds for achieving voting consensus")
    max_handoff_depth: int = Field(default=5, description="Max recursive handoff redirects permitted")
    max_negotiation_retries: int = Field(default=3, description="Max retries if bidding fails to resolve ownership")
    dlq_max_size: int = Field(default=100, description="Dead-Letter Queue maximum capacity limit")
    metrics_retention_days: int = Field(default=30, description="Retain analytics metrics history for N days")

    class Config:
        env_prefix = "NOVA_COLLABORATION_"
        case_sensitive = False
