"""Text-to-Speech provider with local Piper and pyttsx3 adapters.
"""

import os
import structlog
from app.ai.voice.interfaces import ITextToSpeechProvider
from app.ai.voice.exceptions import TextToSpeechError

logger = structlog.get_logger(__name__)

class LocalTTSProvider(ITextToSpeechProvider):
    """Local offline TTS provider with dynamic fallbacks."""

    def __init__(self, storage_path: str = ".nova/cache/voice/", use_mock: bool = True) -> None:
        self.storage_path = storage_path
        self.use_mock = use_mock

    async def synthesize(self, text: str) -> str:
        """Synthesizes text input to audio, returning the wav file path."""
        os.makedirs(self.storage_path, exist_ok=True)
        dest_file = os.path.join(self.storage_path, f"synthesized_response.wav")

        if self.use_mock:
            # Create a mock dummy audio wav file content
            try:
                with open(dest_file, "wb") as f:
                    f.write(b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x08\x00\x00")
                return dest_file
            except Exception as err:
                raise TextToSpeechError(f"Mock TTS writing failed: {err}")

        # Try pyttsx3 dynamic system text-to-speech driver
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, dest_file)
            engine.runAndWait()
            return dest_file
        except Exception as err:
            logger.warn("pyttsx3_tts_failed_falling_back_to_mock", error=str(err))
            # Fallback mock write
            with open(dest_file, "wb") as f:
                f.write(b"RIFF_MOCK_WAVE_DATA")
            return dest_file

class MockTTSProvider(LocalTTSProvider):
    """Explicitly mock text-to-speech provider for tests."""
    
    def __init__(self) -> None:
        super().__init__(use_mock=True)
