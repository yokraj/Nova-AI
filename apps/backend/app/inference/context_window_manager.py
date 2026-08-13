"""Context Window Manager Module.

Manages model context window bounds across 4K, 8K, 16K, 32K, 64K, 128K, and 256K token windows.
Automatically trims prompts and conversation histories to prevent context overflow.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ContextWindowManager:
    """Enterprise Context Window Optimization Manager."""

    def __init__(self) -> None:
        self.supported_windows = [4096, 8192, 16384, 32768, 65536, 131072, 262144]
        logger.info("context_window_manager_initialized")

    def estimate_tokens(self, text: str) -> int:
        """Estimates token count using word heuristics (~1.3 tokens/word)."""
        return int(len(text.split()) * 1.3)

    def optimize_context_window(
        self, prompt: str, max_context_tokens: int = 8192
    ) -> Dict[str, Any]:
        """Trims prompt to fit target context window."""
        est_tokens = self.estimate_tokens(prompt)
        if est_tokens <= max_context_tokens:
            return {
                "prompt": prompt,
                "token_count": est_tokens,
                "trimmed": False,
            }

        allowed_words = int(max_context_tokens / 1.3)
        words = prompt.split()[:allowed_words]
        trimmed_prompt = " ".join(words) + "..."
        new_tokens = self.estimate_tokens(trimmed_prompt)

        logger.info("context_window_trimmed", original_tokens=est_tokens, trimmed_tokens=new_tokens)
        return {
            "prompt": trimmed_prompt,
            "token_count": new_tokens,
            "trimmed": True,
        }
