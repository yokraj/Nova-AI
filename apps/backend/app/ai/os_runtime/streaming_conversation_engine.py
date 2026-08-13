"""Speculative Early Reasoning Engine on Partial Transcription.
"""

from app.ai.os_runtime.interfaces import IStreamingConversationEngine
from app.ai.os_runtime.models import EarlyReasoningResult


class StreamingConversationEngine(IStreamingConversationEngine):
    """Initiates speculative reasoning and early planning before the user finishes speaking."""

    async def evaluate_partial(self, partial_text: str) -> EarlyReasoningResult:
        """Evaluates incremental partial transcription tokens for early intent prediction."""
        text_lower = partial_text.lower()
        if "vs code" in text_lower or "code" in text_lower:
            speculative_action = "Launch Visual Studio Code"
        elif "browser" in text_lower or "chrome" in text_lower:
            speculative_action = "Launch Google Chrome Browser"
        else:
            speculative_action = "Prepare general conversation routing"

        return EarlyReasoningResult(
            partial_intent=partial_text,
            speculative_action=speculative_action,
            ready_for_execution=len(partial_text.split()) >= 4,
        )
