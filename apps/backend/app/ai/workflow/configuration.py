"""Configuration settings profiles for the Workflow Orchestration Engine.
"""

from pydantic_settings import BaseSettings
from pydantic import Field

class WorkflowConfiguration(BaseSettings):
    """Configuration settings for workflow scheduling and execution bounds."""

    step_timeout_seconds: int = Field(default=300, description="Max execution duration in seconds for a single step")
    max_step_retries: int = Field(default=3, description="Max retry attempts for transient step failures")
    backoff_factor: float = Field(default=1.5, description="Multiplier for step retry exponential backoffs")
    checkpoint_rate: int = Field(default=1, description="Interval of steps completed before saving a checkpoint")
    storage_path: str = Field(default="./data/workflows", description="Local directory path to save serialized states")

    class Config:
        env_prefix = "NOVA_WORKFLOW_"
        case_sensitive = False
