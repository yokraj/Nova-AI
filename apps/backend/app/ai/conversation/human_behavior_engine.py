"""Human Behavior Engine detecting hesitation, thinking pauses, unfinished sentences, and idle state.
"""

from typing import Any, Dict


class HumanBehaviorEngine:
    """Analyzes human speech patterns, pauses, and hesitation signals."""

    def analyze_behavior(self, text: str, pause_duration_ms: float = 0.0) -> Dict[str, Any]:
        """Analyzes speech input for hesitation markers and pauses.

        Args:
            text: Utterance text string.
            pause_duration_ms: Duration of pre-utterance silence in milliseconds.

        Returns:
            Dictionary containing hesitation_detected, thinking_pause, unfinished, and idle.
        """
        t_lower = text.lower()
        hesitation = any(w in t_lower for w in ["um", "uh", "err", "hmm", "well..."])
        unfinished = text.endswith("...") or text.endswith("-")
        thinking_pause = pause_duration_ms > 1500.0

        return {
            "hesitation_detected": hesitation,
            "thinking_pause": thinking_pause,
            "unfinished_sentence": unfinished,
            "idle_state": pause_duration_ms > 10000.0,
        }
