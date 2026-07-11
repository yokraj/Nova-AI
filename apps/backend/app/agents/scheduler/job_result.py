"""JobResult schemas tracking execution outcomes.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class JobResult(BaseModel):
    """Contains outcome data resulting from job execution."""

    success: bool = Field(..., description="True if job completed without failures.")
    output: Optional[Any] = Field(None, description="Final response output returned by agent execution.")
    execution_time: float = Field(..., description="Duration of job execution in seconds.")
    retries: int = Field(0, description="Number of retry attempts executed.")
    errors: List[str] = Field(default_factory=list, description="Error messages captured during execution.")
