"""Abstract base contracts for Human-Like Conversation & EI Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.ai.conversation.models import (
    ConversationHealth,
    ConversationMetrics,
    ConversationResponsePayload,
    ConversationSession,
    EmotionMetadata,
    PersonalityMetadata,
    PersonalityProfileType,
)


class IEmotionEngine(ABC):
    """Emotion Engine contract for emotion detection and speech adaptation."""

    @abstractmethod
    def detect_emotion(self, text: str) -> EmotionMetadata:
        """Detects user emotion state from text utterance."""
        pass

    @abstractmethod
    def adapt_speech_parameters(self, emotion: EmotionMetadata) -> Dict[str, float]:
        """Calculates speech synthesis rate and pitch adjustments."""
        pass


class IPersonalityEngine(ABC):
    """Personality Engine contract for personality profile management."""

    @abstractmethod
    def get_profile(self, profile_type: PersonalityProfileType) -> PersonalityMetadata:
        """Retrieves profile specs by profile_type enum."""
        pass

    @abstractmethod
    def set_active_profile(self, session_id: str, profile_type: PersonalityProfileType) -> PersonalityMetadata:
        """Sets active personality profile for session."""
        pass


class IDialogManager(ABC):
    """Dialog Manager contract handling multi-turn state, topics, and pronouns."""

    @abstractmethod
    def process_utterance(self, session_id: str, text: str) -> Dict[str, Any]:
        """Processes turn utterance and updates dialog state."""
        pass


class IInterruptionManager(ABC):
    """Interruption Manager contract handling human barge-in and cancellation."""

    @abstractmethod
    def handle_interruption(self, session_id: str) -> bool:
        """Triggers barge-in cancellation for active speech output."""
        pass


class IStreamingManager(ABC):
    """Streaming Manager contract for token and voice streaming."""

    @abstractmethod
    async def stream_response(self, session_id: str, prompt: str) -> AsyncGenerator[str, None]:
        """Streams text chunks for prompt."""
        pass


class IConversationManager(ABC):
    """Conversation Session Manager contract."""

    @abstractmethod
    def create_session(self, user_id: str = "user_primary") -> ConversationSession:
        """Creates a new conversation session."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieves session by ID."""
        pass


class IUniversalConversationEngine(ABC):
    """Central Universal Conversation Engine facade contract."""

    @abstractmethod
    async def conversation(self, prompt: str, session_id: Optional[str] = None, **kwargs: Any) -> ConversationResponsePayload:
        """Executes multi-turn conversation turn."""
        pass

    @abstractmethod
    async def continue_conversation(self, session_id: str, prompt: str, **kwargs: Any) -> ConversationResponsePayload:
        """Continues active conversation session."""
        pass

    @abstractmethod
    async def conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves turn history."""
        pass

    @abstractmethod
    async def conversation_summary(self, session_id: str) -> str:
        """Retrieves conversation summary."""
        pass

    @abstractmethod
    async def conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieves cognitive context snapshot."""
        pass

    @abstractmethod
    async def set_personality(self, personality: str, session_id: Optional[str] = None) -> PersonalityMetadata:
        """Sets active personality profile."""
        pass

    @abstractmethod
    async def current_emotion(self, session_id: str) -> EmotionMetadata:
        """Retrieves current detected emotion."""
        pass

    @abstractmethod
    async def interrupt_response(self, session_id: str) -> bool:
        """Interrupts active streaming speech response."""
        pass
