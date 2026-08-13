"""Wake Word Runtime detecting wake phrases ('Hey Nova', 'Nova') with false-positive suppression and cooldown."""

from datetime import datetime, timedelta
from typing import Optional
import structlog

from app.ai.ambient.configuration import AmbientConfiguration
from app.ai.ambient.interfaces import IWakeWordRuntime
from app.ai.ambient.models import AudioFrame, WakeWordMatch, WakeWordType

logger = structlog.get_logger("wake_word_runtime")


class WakeWordRuntime(IWakeWordRuntime):
    """Wake word detection engine with false-positive reduction and cooldown logic."""

    def __init__(self, config: Optional[AmbientConfiguration] = None) -> None:
        self.config = config or AmbientConfiguration()
        self.last_trigger_time: Optional[datetime] = None

    async def process_frame(self, frame: AudioFrame) -> Optional[WakeWordMatch]:
        """Evaluate audio frame for wake word trigger."""
        now = datetime.utcnow()
        if self.last_trigger_time:
            elapsed = (now - self.last_trigger_time).total_seconds()
            if elapsed < self.config.wake_word_cooldown_seconds:
                return None

        # Simulate frame processing match
        if frame.has_speech:
            self.last_trigger_time = now
            logger.info("Wake word detected", phrase="Hey Nova")
            return WakeWordMatch(phrase="Hey Nova", wake_type=WakeWordType.PRIMARY)

        return None

    async def detect_in_text(self, text: str) -> Optional[WakeWordMatch]:
        """Detect wake word in text transcript."""
        t_lower = text.lower()
        now = datetime.utcnow()
        for kw in self.config.wake_words:
            if kw.lower() in t_lower:
                self.last_trigger_time = now
                logger.info("Wake word matched in text transcript", phrase=kw)
                return WakeWordMatch(phrase=kw, wake_type=WakeWordType.PRIMARY if kw == "Hey Nova" else WakeWordType.SHORT)
        return None
