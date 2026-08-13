"""Token Usage Tracker Module.

Tracks prompt tokens, completion tokens, total tokens, average tokens, peak tokens, and context utilization.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class TokenUsageTracker:
    """Enterprise Token Usage & Utilization Tracker."""

    def __init__(self) -> None:
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_tokens: int = 0
        self.peak_tokens: int = 0
        logger.info("token_usage_tracker_initialized")

    def record_usage(self, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        """Records token usage for an inference request."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        req_total = prompt_tokens + completion_tokens
        self.total_tokens += req_total

        if req_total > self.peak_tokens:
            self.peak_tokens = req_total

        logger.info("token_usage_recorded", prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": req_total,
        }
