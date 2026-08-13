"""Speech Barge-in Interruption Engine.
"""

from app.ai.os_runtime.interfaces import IInterruptionEngine


class InterruptionEngine(IInterruptionEngine):
    """Detects speech barge-in, immediately pauses TTS waveform output, and allows user command modification/cancel."""

    def __init__(self) -> None:
        self.tts_speaking: bool = False
        self.interrupted_count: int = 0

    async def handle_barge_in(self) -> bool:
        """Immediately stops active TTS playback when user starts speaking."""
        self.tts_speaking = False
        self.interrupted_count += 1
        return True

    def set_speaking_state(self, speaking: bool) -> None:
        self.tts_speaking = speaking
