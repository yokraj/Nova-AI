"""Token Manager tracking token consumption, latency, throughput, and estimated costs.
"""

from app.ai.models.interfaces import ITokenManager
from app.ai.models.models import TokenUsage


class TokenManager(ITokenManager):
    """Token Manager logging token accounting metrics across model invocations."""

    def __init__(self) -> None:
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost = 0.0

    def record_usage(self, usage: TokenUsage) -> None:
        """Logs token usage metrics.

        Args:
            usage: TokenUsage model instance.
        """
        self._total_prompt_tokens += usage.prompt_tokens
        self._total_completion_tokens += usage.completion_tokens
        self._total_cost += usage.estimated_cost

    def get_total_usage(self) -> TokenUsage:
        """Returns cumulative token accounting snapshot."""
        return TokenUsage(
            prompt_tokens=self._total_prompt_tokens,
            completion_tokens=self._total_completion_tokens,
            total_tokens=self._total_prompt_tokens + self._total_completion_tokens,
            estimated_cost=self._total_cost,
        )
