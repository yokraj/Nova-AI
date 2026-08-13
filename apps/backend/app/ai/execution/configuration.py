"""Configuration settings for the Autonomous Skill Execution Runtime."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExecutionConfiguration(BaseSettings):
    """Central configuration for execution runtime, queues, checkpoints, and resource monitoring."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_EXECUTION_",
        case_sensitive=False,
        extra="ignore",
    )

    max_concurrent_missions: int = Field(
        default=5,
        description="Maximum concurrent active missions running in the execution runtime.",
    )
    checkpoint_dir: str = Field(
        default="./data/checkpoints",
        description="Directory path for persisting mission checkpoint state files.",
    )
    default_timeout_seconds: float = Field(
        default=120.0,
        description="Default step execution timeout before triggering recovery routines.",
    )
    enable_auto_recovery: bool = Field(
        default=True,
        description="Whether to automatically attempt recovery on step failures.",
    )
    max_step_retries: int = Field(
        default=3,
        description="Maximum retry attempts per failed execution step.",
    )
    enable_transactions: bool = Field(
        default=True,
        description="Whether to enable atomic multi-step rollback transactions.",
    )
    max_cpu_percent: float = Field(
        default=90.0,
        description="Maximum CPU percentage threshold before throttling task execution.",
    )
    max_memory_percent: float = Field(
        default=90.0,
        description="Maximum RAM percentage threshold before throttling task execution.",
    )
