"""Text-to-Speech provider with local neural and SAPI adapters.
"""

import os
import structlog
from app.ai.voice.interfaces import ITextToSpeechProvider
from app.ai.voice.exceptions import TextToSpeechError
from app.ai.voice.tts_engine import LocalTTSEngine

logger = structlog.get_logger(__name__)


class LocalTTSProvider(ITextToSpeechProvider):
    """Local offline TTS provider with dynamic fallbacks."""

    def __init__(self, storage_path: str = ".nova/cache/voice/", use_mock: bool = False) -> None:
        self.storage_path = storage_path
        self.use_mock = use_mock
        self._engine = LocalTTSEngine(storage_path=storage_path)

    async def synthesize(self, text: str) -> str:
        """Synthesizes text input to audio, returning the wav file path."""
        if not text or not text.strip():
            raise TextToSpeechError("Text cannot be empty.")

        os.makedirs(self.storage_path, exist_ok=True)
        dest_file = os.path.join(self.storage_path, "synthesized_response.wav")

        if self.use_mock:
            # Create a mock dummy audio wav file content for unit testing
            try:
                with open(dest_file, "wb") as f:
                    f.write(b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x08\x00\x00")
                return dest_file
            except Exception as err:
                raise TextToSpeechError(f"Mock TTS writing failed: {err}")

        # Real synthesis via LocalTTSEngine
        return await self._engine.synthesize(text)


class MockTTSProvider(LocalTTSProvider):
    """Explicitly mock text-to-speech provider for tests."""

    def __init__(self) -> None:
        super().__init__(use_mock=True)
