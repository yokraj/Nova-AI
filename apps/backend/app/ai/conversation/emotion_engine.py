"""Emotion Engine adapting voice speech rate, pitch, tone, and response verbosity based on detected emotion.
"""

from typing import Dict
from app.ai.conversation.emotion_detector import EmotionDetector
from app.ai.conversation.interfaces import IEmotionEngine
from app.ai.conversation.models import EmotionMetadata


class EmotionEngine(IEmotionEngine):
    """Orchestrates emotion detection and calculates voice speech adaptation parameters."""

    def __init__(self) -> None:
        self.detector = EmotionDetector()

    def detect_emotion(self, text: str) -> EmotionMetadata:
        """Delegates text analysis to EmotionDetector."""
        return self.detector.detect_emotion(text)

    def adapt_speech_parameters(self, emotion: EmotionMetadata) -> Dict[str, float]:
        """Calculates voice synthesis speech rate multiplier and pitch shift."""
        return {
            "rate_multiplier": emotion.speech_rate_multiplier,
            "pitch_shift": emotion.pitch_shift,
            "confidence": emotion.confidence,
        }
