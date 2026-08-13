"""Custom exceptions for the Enterprise Voice Intelligence Layer.
"""

from app.ai.exceptions import AiGatewayException

class VoiceEngineError(AiGatewayException):
    """Base exception for all voice operations."""
    pass

class SpeechRecognitionError(VoiceEngineError):
    """Raised when speech transcription fails."""
    pass

class TextToSpeechError(VoiceEngineError):
    """Raised when text to speech synthesis fails."""
    pass

class WakeWordError(VoiceEngineError):
    """Raised when wake word detection fails."""
    pass

class VoiceSessionError(VoiceEngineError):
    """Raised when voice session management fails."""
    pass
