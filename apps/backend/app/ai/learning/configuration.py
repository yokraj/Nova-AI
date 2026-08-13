"""Configuration settings for the Continuous Learning & Shared Experience Engine."""

from pydantic import Field
from pydantic_settings import BaseSettings


class LearningConfiguration(BaseSettings):
    """Configuration for experience storage, pattern detection, and strategy management."""

    storage_path: str = Field(
        default="./data/learning",
        description="Local directory path for serialised experience and strategy data."
    )
    max_experiences: int = Field(
        default=10_000,
        description="Maximum number of experience records retained in the in-memory store."
    )
    pattern_min_occurrences: int = Field(
        default=2,
        description="Minimum occurrence count before an event is promoted to a detected pattern."
    )
    strategy_max_versions: int = Field(
        default=10,
        description="Maximum retained versions per strategy before oldest is evicted."
    )
    enable_cross_agent_sharing: bool = Field(
        default=True,
        description="Whether agents share learned strategies and experience across the team."
    )
    knowledge_reuse_threshold: float = Field(
        default=0.7,
        description="Minimum strategy success_rate required before it qualifies as reusable."
    )
    recommendation_confidence_threshold: float = Field(
        default=0.6,
        description="Minimum confidence score a recommendation must reach before it is returned."
    )

    class Config:
        env_prefix = "NOVA_LEARNING_"
        case_sensitive = False
