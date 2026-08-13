"""Speech Coordinator configuring TTS synthesis parameters based on emotion and personality.
"""

from typing import Any, Dict
from app.ai.conversation.models import EmotionMetadata, PersonalityMetadata


class SpeechCoordinator:
    """Coordinates voice parameters (rate, pitch, volume, voice_id) for local TTS engines."""

    def prepare_speech_config(self, emotion: EmotionMetadata, personality: PersonalityMetadata) -> Dict[str, Any]:
        """Generates voice synthesis configuration dict.

        Args:
            emotion: EmotionMetadata instance.
            personality: PersonalityMetadata instance.

        Returns:
            Dictionary containing voice_id, rate_multiplier, pitch_shift, and volume.
        """
        return {
            "voice_id": personality.voice_id,
            "rate_multiplier": emotion.speech_rate_multiplier,
            "pitch_shift": emotion.pitch_shift,
            "volume": 1.0,
            "tone_descriptor": emotion.tone_descriptor,
        }
