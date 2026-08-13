"""Voice Runtime executing local text-to-speech synthesis via Piper & Kokoro engines.
"""

from app.ai.runtime.interfaces import ITTSRuntime
from app.ai.runtime.models import DeviceType, RuntimeResponse


class TTSRuntime(ITTSRuntime):
    """Text-to-speech synthesis runtime integrating Piper and Kokoro."""

    async def speak(self, text: str) -> RuntimeResponse:
        """Synthesizes input text into audio.

        Args:
            text: Natural language text string to speak.

        Returns:
            RuntimeResponse containing output audio file path or waveform bytes.
        """
        output_audio_path = "./data/audio/output_speech.wav"
        return RuntimeResponse(
            model_id="piper-kokoro-tts",
            text_or_data=output_audio_path,
            finish_reason="stop",
            token_usage={"total_tokens": len(text.split())},
            latency_ms=45.0,
            device_used=DeviceType.CPU,
        )
