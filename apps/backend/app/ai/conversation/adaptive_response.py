"""Adaptive Response Formatter formatting response style based on emotion and personality.
"""

from app.ai.conversation.models import EmotionMetadata, PersonalityMetadata


class AdaptiveResponseFormatter:
    """Formats response text, tone, and verbosity based on user emotion and active personality profile."""

    def format_response(self, text: str, emotion: EmotionMetadata, personality: PersonalityMetadata) -> str:
        """Formats response text string according to emotion and personality guidance.

        Args:
            text: Raw generated response text.
            emotion: User EmotionMetadata.
            personality: Active PersonalityMetadata.

        Returns:
            Formatted response text string.
        """
        prefix = ""
        if emotion.primary_emotion.value == "frustrated":
            prefix = "[Reassuring & Calm] "
        elif emotion.primary_emotion.value == "urgent":
            prefix = "[Urgent & Concise] "
        elif emotion.primary_emotion.value == "confused":
            prefix = "[Step-by-Step Explanation] "

        profile_tag = f"({personality.name})"
        return f"{prefix}{text} {profile_tag}"
