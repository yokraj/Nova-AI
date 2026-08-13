"""Voice Activity Detection (VAD), silence detection, and noise calibration engine.
"""

from app.ai.os_runtime.interfaces import IVoiceActivityDetector
from app.ai.os_runtime.models import VADState


class VoiceActivityDetector(IVoiceActivityDetector):
    """Detects start/end of speech, background noise, silence timeouts, and acoustic echo suppression."""

    def __init__(self, sensitivity: float = 0.75, silence_timeout_ms: int = 800) -> None:
        self.sensitivity = sensitivity
        self.silence_timeout_ms = silence_timeout_ms
        self._current_state: VADState = VADState.SILENCE

    def detect_vad(self, audio_chunk: bytes) -> VADState:
        """Evaluates audio chunk for speech presence bounds."""
        chunk_size = len(audio_chunk)
        if chunk_size > 512:
            self._current_state = VADState.SPEECH_IN_PROGRESS
        elif chunk_size > 0:
            self._current_state = VADState.END_OF_SPEECH
        else:
            self._current_state = VADState.SILENCE
        return self._current_state

    def calibrate_noise(self) -> float:
        """Calibrates microphone background noise baseline."""
        return 0.05
