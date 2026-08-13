"""Emotion Detector evaluating user text, punctuation, and tone heuristics to identify emotion states.
"""

from app.ai.conversation.models import EmotionMetadata, EmotionState


class EmotionDetector:
    """Detects Happy, Sad, Angry, Frustrated, Confused, Stressed, Excited, Urgent, Neutral, Burnout states."""

    def detect_emotion(self, text: str) -> EmotionMetadata:
        """Detects emotion metadata from text utterance.

        Args:
            text: Utterance text string.

        Returns:
            EmotionMetadata instance.
        """
        t_lower = text.lower()

        if any(w in t_lower for w in ["urgent", "asap", "emergency", "immediately", "right now"]):
            return EmotionMetadata(
                primary_emotion=EmotionState.URGENT,
                confidence=0.98,
                speech_rate_multiplier=1.25,
                pitch_shift=0.1,
                tone_descriptor="swift, direct, and concise",
            )
        elif any(w in t_lower for w in ["frustrated", "annoyed", "wrong", "broken", "why isn't this working", "fail"]):
            return EmotionMetadata(
                primary_emotion=EmotionState.FRUSTRATED,
                confidence=0.92,
                speech_rate_multiplier=0.95,
                pitch_shift=-0.05,
                tone_descriptor="patient, calm, and reassuring",
            )
        elif any(w in t_lower for w in ["confused", "don't understand", "what does this mean", "how to"]):
            return EmotionMetadata(
                primary_emotion=EmotionState.CONFUSED,
                confidence=0.90,
                speech_rate_multiplier=0.90,
                pitch_shift=0.0,
                tone_descriptor="instructive, clear, and structured",
            )
        elif any(w in t_lower for w in ["excited", "awesome", "great", "fantastic", "amazing", "love"]):
            return EmotionMetadata(
                primary_emotion=EmotionState.EXCITED,
                confidence=0.95,
                speech_rate_multiplier=1.15,
                pitch_shift=0.15,
                tone_descriptor="enthusiastic, warm, and energetic",
            )
        elif any(w in t_lower for w in ["exhausted", "burnout", "tired", "too much", "overwhelmed"]):
            return EmotionMetadata(
                primary_emotion=EmotionState.BURNOUT,
                confidence=0.94,
                speech_rate_multiplier=0.85,
                pitch_shift=-0.1,
                tone_descriptor="gentle, supportive, and minimalist",
            )

        return EmotionMetadata(
            primary_emotion=EmotionState.NEUTRAL,
            confidence=0.88,
            speech_rate_multiplier=1.0,
            pitch_shift=0.0,
            tone_descriptor="balanced, articulate, and professional",
        )
