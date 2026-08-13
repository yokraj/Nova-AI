"""Ambient Manager unifying microphone listener, wake word runtime, desktop monitors, and proactive assistant."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.ambient.attention_manager import AttentionManager
from app.ai.ambient.context_pipeline import ContextPipeline
from app.ai.ambient.conversation_manager import ConversationManager
from app.ai.ambient.interruption_manager import InterruptionManager
from app.ai.ambient.microphone_listener import MicrophoneListener
from app.ai.ambient.models import DesktopContextSnapshot, ProactiveSuggestion
from app.ai.ambient.proactive_assistant import ProactiveAssistant
from app.ai.ambient.wake_word_runtime import WakeWordRuntime

logger = structlog.get_logger("ambient_manager")


class AmbientManager:
    """High-level Ambient Orchestrator connecting microphone, wake word, desktop context, and proactive alerts."""

    def __init__(self) -> None:
        self.mic = MicrophoneListener()
        self.wake_word = WakeWordRuntime()
        self.conversation = ConversationManager()
        self.context_pipeline = ContextPipeline()
        self.proactive = ProactiveAssistant()
        self.interruption = InterruptionManager()
        self.attention = AttentionManager()

    async def get_proactive_suggestions(self) -> List[ProactiveSuggestion]:
        """Capture desktop snapshot and return gated proactive suggestions."""
        snapshot: DesktopContextSnapshot = await self.context_pipeline.get_composite_snapshot()
        raw_sug = await self.proactive.evaluate_context(snapshot)
        should_alert = await self.interruption.should_interrupt(in_meeting=snapshot.is_in_meeting)
        if not should_alert:
            logger.info("Filtered non-critical proactive suggestions during active meeting")
            return [s for s in raw_sug if s.category == "meeting"]
        return raw_sug
