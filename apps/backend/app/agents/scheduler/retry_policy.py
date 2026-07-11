"""RetryPolicy configuration schemas.
"""

from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    """Configuration policies for job execution retries."""

    max_retries: int = Field(3, description="Maximum number of retry attempts allowed.")
    exponential_backoff: bool = Field(True, description="True to double the delay on each subsequent retry.")
    retry_delay: float = Field(1.0, description="Base delay duration in seconds between retry attempts.")
