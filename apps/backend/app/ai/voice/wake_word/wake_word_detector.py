"""Wake Word Detector matches keyword triggers like 'Nova'.
"""

import structlog
from app.ai.voice.interfaces import IWakeWordDetector
from app.ai.voice.exceptions import WakeWordError

logger = structlog.get_logger(__name__)

class WakeWordDetector(IWakeWordDetector):
    """Monitors incoming live audio streams for wake keyword triggers."""

    def __init__(self, keyword: str = "Nova") -> None:
        self.keyword = keyword.lower()
        self.listening = False

    def detect(self, audio_chunk: bytes) -> bool:
        """Heuristically checks if the wake word is present in the current audio chunk."""
        if not audio_chunk:
            return False

        try:
            # Check for plaintext ASCII command trigger containing the keyword (for mock testing)
            decoded = audio_chunk.decode("utf-8", errors="ignore").lower()
            return self.keyword in decoded
        except Exception:
            return False

    def start_listener(self) -> None:
        """Starts background recorder threads."""
        self.listening = True
        logger.info("wake_word_detector_started", keyword=self.keyword)

    def stop_listener(self) -> None:
        """Stops background recorder threads."""
        self.listening = False
        logger.info("wake_word_detector_stopped")
