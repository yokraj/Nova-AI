"""Mock Conversation Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict, Optional
from app.ai.conversation.models import (
    ConversationResponsePayload,
    EmotionMetadata,
    EmotionState,
    PersonalityMetadata,
    PersonalityProfileType,
)


class MockConversationProvider:
    """Mock Conversation Provider returning deterministic test responses."""

    async def mock_conversation(self, prompt: str, session_id: str = "mock_sess_01") -> ConversationResponsePayload:
        return ConversationResponsePayload(
            session_id=session_id,
            text_response=f"[Mock Conversation Response] Output for: '{prompt}'",
            audio_output_path="./data/audio/mock_speech.wav",
            emotion=EmotionMetadata(primary_emotion=EmotionState.NEUTRAL),
            personality=PersonalityMetadata(profile_type=PersonalityProfileType.DEVELOPER),
            latency_ms=25.0,
        )
