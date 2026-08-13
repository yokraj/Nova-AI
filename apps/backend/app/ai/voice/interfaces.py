"""Interface contracts for voice components.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from app.ai.voice.models import SpeechResult, VoiceSession

class ISpeechRecognizer(ABC):
    """Abstract interface for speech transcription."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> SpeechResult:
        """Converts audio signals to text transcripts."""
        pass

class ITextToSpeechProvider(ABC):
    """Abstract interface for text-to-speech generation."""

    @abstractmethod
    async def synthesize(self, text: str) -> str:
        """Converts text response to a synthesized local audio file path."""
        pass

class IWakeWordDetector(ABC):
    """Abstract interface for wake word keyword trigger detections."""

    @abstractmethod
    def detect(self, audio_chunk: bytes) -> bool:
        """Detects if configured wake keyword was spoken in the audio chunk."""
        pass

class IVoiceSessionManager(ABC):
    """Abstract interface for active voice listener sessions."""

    @abstractmethod
    def create_session(self) -> VoiceSession:
        """Initializes a new listener session."""
        pass

    @abstractmethod
    def close_session(self, session_id: UUID) -> None:
        """Performs cleanup and closes session registry."""
        pass
