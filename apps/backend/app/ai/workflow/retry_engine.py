"""Retry Engine calculating backoff limits for transient failures.
"""

import time
from app.ai.workflow.models import WorkflowStep

class RetryEngine:
    """Manages retry limits and backoff increments."""

    def should_retry(self, step: WorkflowStep, max_retries: int) -> bool:
        """Returns True if step failed but hasn't reached max retries limit."""
        return step.retry_count < max_retries

    def get_backoff_delay(self, retry_count: int, factor: float = 1.5) -> float:
        """Returns exponential backoff sleep delay seconds."""
        return factor ** retry_count
