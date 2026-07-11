"""MetricsCollector tracking execution stats and counters.
"""

from typing import Dict
from pydantic import BaseModel, Field


class MetricsCollector(BaseModel):
    """Maintains metrics counters for agent executions."""

    execution_count: int = Field(0)
    execution_duration: float = Field(0.0)
    average_duration: float = Field(0.0)
    retry_count: int = Field(0)
    failure_count: int = Field(0)
    success_count: int = Field(0)
    token_usage: int = Field(0)
    memory_usage: float = Field(0.0)
    cpu_usage: float = Field(0.0)
    gpu_usage: float = Field(0.0)

    def record_execution(self, duration: float, success: bool, retries: int = 0) -> None:
        """Records telemetry details from a task execution.

        Args:
            duration: Active duration.
            success: Execution status.
            retries: Retry attempts.
        """
        self.execution_count += 1
        self.execution_duration += duration
        self.retry_count += retries
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.average_duration = self.execution_duration / self.execution_count
