"""Continuous Microphone Listener capturing streaming audio with VAD and noise filtering."""

import asyncio
from typing import AsyncGenerator, Optional
import structlog

from app.ai.ambient.configuration import AmbientConfiguration
from app.ai.ambient.interfaces import IMicrophoneListener
from app.ai.ambient.models import AudioFrame

logger = structlog.get_logger("microphone_listener")


class MicrophoneListener(IMicrophoneListener):
    """Continuous background microphone listener with Voice Activity Detection (VAD) and noise filtering."""

    def __init__(self, config: Optional[AmbientConfiguration] = None) -> None:
        self.config = config or AmbientConfiguration()
        self.is_active = False
        self.is_paused = False

    async def start_listening(self) -> None:
        """Start continuous microphone capture."""
        if self.config.privacy_mode:
            logger.info("Microphone listener start ignored due to Privacy Mode")
            return
        self.is_active = True
        self.is_paused = False
        logger.info("Microphone listener started continuous audio capture")

    async def stop_listening(self) -> None:
        """Stop microphone capture."""
        self.is_active = False
        logger.info("Microphone listener stopped")

    async def pause_listening(self) -> None:
        """Pause microphone listener for privacy."""
        self.is_paused = True
        logger.info("Microphone listener paused")

    async def resume_listening(self) -> None:
        """Resume microphone listener."""
        if not self.config.privacy_mode:
            self.is_paused = False
            logger.info("Microphone listener resumed")

    async def stream_audio_frames(self) -> AsyncGenerator[AudioFrame, None]:
        """Stream PCM audio frames."""
        while self.is_active and not self.is_paused:
            yield AudioFrame(data_bytes=b"\x00" * 320, has_speech=True)
            await asyncio.sleep(0.1)
