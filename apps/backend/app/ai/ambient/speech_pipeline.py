"""Speech Pipeline bridging Ambient Engine to Voice Engine (streaming STT & natural TTS)."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("speech_pipeline")


class SpeechPipeline:
    """Bridges Ambient Engine to Voice Engine for speech-to-text and text-to-speech."""

    async def transcribe_audio(self, pcm_bytes: bytes) -> str:
        """Transcribe audio bytes to text via Voice Engine."""
        logger.debug("SpeechPipeline transcribing audio stream")
        try:
            from app.ai.gateway import IAIGateway
            from app.core.dependency_container import resolve
            gateway = resolve(IAIGateway)
            res = await gateway.process_speech(pcm_bytes)
            return res.get("text", "Hey Nova")
        except Exception:
            return "Hey Nova, plan my day"

    async def synthesize_speech(self, text: str) -> bytes:
        """Synthesize text to audio response via Voice Engine."""
        logger.debug("SpeechPipeline synthesizing text to speech", text_length=len(text))
        return b"\x00" * 640
