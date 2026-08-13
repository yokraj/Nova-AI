"""Memory Compressor summarizes long conversation histories.
"""

from typing import List

class MemoryCompressor:
    """Condenses list of dialogue items into compact overview descriptions."""

    def compress_memories(self, conversation_turns: List[str]) -> str:
        """Heuristically summarizes conversation items."""
        if not conversation_turns:
            return ""

        decisions = []
        for turn in conversation_turns:
            lower = turn.lower()
            if "decide" in lower or "prefer" in lower or "use" in lower or "want" in lower:
                decisions.append(turn)

        summary_prefix = "Summary of conversation decisions:\n"
        if decisions:
            return summary_prefix + "\n".join(decisions)
        
        # Fallback to general truncation
        return summary_prefix + f"Truncated history of {len(conversation_turns)} turns."
