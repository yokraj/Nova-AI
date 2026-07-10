"""Concrete implementation of token counting services for chat contents.
"""

from typing import Any, Dict
from app.conversation.services.interfaces import ITokenCounter


class TokenCounter(ITokenCounter):
    """Calculates token counts for raw text using model-specific encoders or estimators."""

    def count_tokens(self, text: str, model_name: str) -> int:
        """Estimates token counts for a text block using model tiktoken or fallback rules.

        Args:
            text: The text to analyze.
            model_name: The target LLM model name.

        Returns:
            The estimated token count.
        """
        if not text:
            return 0
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(model_name)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: estimate ~4 characters per token
            return max(1, len(text) // 4)

    def count_message_tokens(self, message: Dict[str, Any], model_name: str) -> int:
        """Estimates token counts for a structured chat message payload.

        Args:
            message: Dictionary containing message fields like role and content.
            model_name: The target LLM model name.

        Returns:
            Estimated token count.
        """
        content = message.get("content", "") or ""
        role = message.get("role", "") or ""
        # 4 tokens formatting overhead per message (role tag + structure)
        return self.count_tokens(content, model_name) + 4
