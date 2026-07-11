"""ExecutionMetrics details tracking metrics telemetry parameters.
"""

from pydantic import BaseModel, Field


class ExecutionMetrics(BaseModel):
    """Execution performance metrics telemetry tracking."""

    execution_time: float = Field(0.0, description="Execution duration in seconds.")
    retry_count: int = Field(0, description="Total retry attempts performed.")
    memory_usage: float = Field(0.0, description="Placeholder for memory usage in MB.")
    cpu_usage: float = Field(0.0, description="Placeholder for CPU usage percentage.")
    token_usage: int = Field(0, description="Placeholder for LLM token usage.")
