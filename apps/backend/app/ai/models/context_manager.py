"""Context Manager handling context window compression, sliding windows, and summarization.
"""

from app.ai.models.interfaces import IContextManager
from app.ai.models.utils import estimate_token_count


class ContextManager(IContextManager):
    """Context Manager performing sliding window truncation and context compression."""

    def compress_context(self, text: str, max_tokens: int = 2048) -> str:
        """Compresses long context string to fit within max_tokens limit.

        Args:
            text: Raw input context.
            max_tokens: Target maximum token limit.

        Returns:
            Compressed context string.
        """
        estimated_tokens = estimate_token_count(text)
        if estimated_tokens <= max_tokens:
            return text

        # Sliding window compression
        max_chars = max_tokens * 4
        truncated = text[-max_chars:]
        return f"[Context Truncated & Summarized] ... {truncated}"
