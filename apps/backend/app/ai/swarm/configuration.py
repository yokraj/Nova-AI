"""Configuration settings for Multi-Agent Collaboration & Swarm Intelligence Engine."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SwarmConfiguration(BaseSettings):
    """Central configuration for swarm intelligence, delegation, voting, and consensus."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_SWARM_",
        case_sensitive=False,
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether swarm intelligence engine is active.",
    )
    max_agents_per_swarm: int = Field(
        default=10,
        description="Maximum concurrent agents allocated to a single swarm mission.",
    )
    consensus_threshold: float = Field(
        default=0.6,
        description="Consensus threshold ratio (e.g. 0.6 = 60% majority).",
    )
    default_voting_strategy: str = Field(
        default="majority",
        description="Default voting strategy ('majority', 'weighted', 'confidence', 'leader').",
    )
    task_timeout_seconds: float = Field(
        default=30.0,
        description="Timeout for individual swarm task execution.",
    )
    max_retry_attempts: int = Field(
        default=3,
        description="Max retry attempts for failed agent task execution.",
    )
