"""TokenHelper estimating token usage limits.
"""

from typing import Optional
from app.ai.gateway.ai_gateway import AIGateway
from app.agent_sdk.ai.exceptions import AIHelperError


class TokenHelper:
    """Lightweight token estimator and truncation helper using gateway limits."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes TokenHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway

    def estimate(self, text: str) -> int:
        """Estimates token count of a given string (approx 4 chars/token).

        Args:
            text: Text to evaluate.

        Returns:
            Estimated count of tokens.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)

    def remaining_context(self, text: str, model_name: str) -> int:
        """Calculates remaining token headroom inside context window limits.

        Args:
            model_name: Identifier of the target model.
            text: Text currently filling the context window.

        Returns:
            Number of remaining tokens available.
        """
        info = self.gateway.model_registry.model(model_name)
        if not info:
            limit = 4096
        else:
            limit = info.context_window

        used = self.estimate(text)
        return max(0, limit - used)

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncates string to fit within specified token limits.

        Args:
            text: String to truncate.
            max_tokens: Target maximum tokens limit.

        Returns:
            Truncated string.
        """
        if not text or max_tokens <= 0:
            return ""

        char_budget = max_tokens * 4
        if len(text) <= char_budget:
            return text
        return text[:char_budget]
