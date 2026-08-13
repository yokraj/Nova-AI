"""Abstract interface contracts for Ambient Intelligence & Continuous Voice Assistant."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.ambient.models import (
    AmbientHealth,
    AmbientMetrics,
    AudioFrame,
    DesktopContextSnapshot,
    ProactiveSuggestion,
    WakeWordMatch,
)


class IMicrophoneListener(ABC):
    """Abstract contract for continuous microphone listening and audio streaming."""

    @abstractmethod
    async def start_listening(self) -> None:
        pass

    @abstractmethod
    async def stop_listening(self) -> None:
        pass

    @abstractmethod
    async def pause_listening(self) -> None:
        pass

    @abstractmethod
    async def resume_listening(self) -> None:
        pass


class IWakeWordRuntime(ABC):
    """Abstract contract for wake word detection."""

    @abstractmethod
    async def process_frame(self, frame: AudioFrame) -> Optional[WakeWordMatch]:
        pass


class IConversationManager(ABC):
    """Abstract contract for multi-turn voice conversation management."""

    @abstractmethod
    async def handle_user_speech(self, text: str) -> Dict[str, Any]:
        pass


class IDesktopContextMonitor(ABC):
    """Abstract contract for desktop awareness monitoring."""

    @abstractmethod
    async def capture_snapshot(self) -> DesktopContextSnapshot:
        pass


class IProactiveAssistant(ABC):
    """Abstract contract for generating proactive suggestions."""

    @abstractmethod
    async def evaluate_context(self, context: DesktopContextSnapshot) -> List[ProactiveSuggestion]:
        pass


class IAmbientEngine(ABC):
    """Abstract contract for central Ambient Intelligence facade."""

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def process_conversation(self, query: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_metrics(self) -> AmbientMetrics:
        pass

    @abstractmethod
    def check_health(self) -> AmbientHealth:
        pass
