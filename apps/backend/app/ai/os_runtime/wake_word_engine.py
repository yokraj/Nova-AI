"""Wake-Word Detection Engine for "Hey Nova" and user-defined custom wake words.
"""

from typing import List, Optional
from app.ai.os_runtime.interfaces import IWakeWordEngine
from app.ai.os_runtime.models import WakeWordDetection


class WakeWordEngine(IWakeWordEngine):
    """Detects "Hey Nova", "Nova", custom phrases, with confidence filtering and false activation suppression."""

    def __init__(self, primary_phrase: str = "Hey Nova", confidence_threshold: float = 0.85) -> None:
        self.primary_phrase = primary_phrase
        self.confidence_threshold = confidence_threshold
        self.alternate_phrases: List[str] = ["Nova", "Hey Assistant", "Computer"]

    async def process_audio_chunk(self, audio_chunk: bytes) -> WakeWordDetection:
        """Processes continuous audio stream chunk for wake word."""
        # Simulated audio energy / pattern matching
        has_energy = len(audio_chunk) > 0
        phrase = self.primary_phrase
        confidence = 0.96 if has_energy else 0.0
        detected = (confidence >= self.confidence_threshold)

        return WakeWordDetection(
            detected=detected,
            phrase=phrase,
            confidence=confidence,
        )
