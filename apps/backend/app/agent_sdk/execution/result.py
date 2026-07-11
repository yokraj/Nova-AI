"""ExecutionResult encapsulating outcomes status of task execution.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field

from app.agent_sdk.execution.metrics import ExecutionMetrics


class ExecutionResult(BaseModel):
    """Result payload detailing the outcome of a runner execution."""

    success: bool = Field(..., description="True if operation completed successfully.")
    status: str = Field("completed", description="Status code (e.g. 'completed', 'failed', 'cancelled').")
    result: Any = Field(None, description="Actual outcome payload.")
    error: Optional[str] = Field(None, description="Error message if failed.")
    duration: float = Field(0.0, description="Execution time in seconds.")
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    logs: List[str] = Field(default_factory=list)
