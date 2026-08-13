"""Central Universal Conversation Engine facade unifying Emotional Intelligence, Personality, and Dialogue.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.conversation.adaptive_response import AdaptiveResponseFormatter
from app.ai.conversation.cache import ConversationCache
from app.ai.conversation.clarification_engine import ClarificationEngine
from app.ai.conversation.configuration import ConversationConfiguration
from app.ai.conversation.conversation_compressor import ConversationCompressor
from app.ai.conversation.conversation_context import CognitiveContextTracker
from app.ai.conversation.conversation_history import ConversationHistoryTracker
from app.ai.conversation.conversation_learning import ConversationLearningEngine
from app.ai.conversation.conversation_manager import ConversationManager
from app.ai.conversation.conversation_memory import ConversationMemory
from app.ai.conversation.conversation_recovery import ConversationRecoveryEngine
from app.ai.conversation.conversation_state import ConversationStateTracker
from app.ai.conversation.conversation_validator import ConversationValidator
from app.ai.conversation.dialog_manager import DialogManager
from app.ai.conversation.emotion_engine import EmotionEngine
from app.ai.conversation.followup_engine import FollowupEngine
from app.ai.conversation.health import ConversationHealthMonitor
from app.ai.conversation.human_behavior_engine import HumanBehaviorEngine
from app.ai.conversation.interfaces import IUniversalConversationEngine
from app.ai.conversation.interruption_manager import InterruptionManager
from app.ai.conversation.metrics import ConversationMetricsTracker
from app.ai.conversation.models import (
    ConversationHealth,
    ConversationMetrics,
    ConversationResponsePayload,
    ConversationTurnRole,
    EmotionMetadata,
    PersonalityMetadata,
    PersonalityProfileType,
)
from app.ai.conversation.personality_engine import PersonalityEngine
from app.ai.conversation.response_generator import ResponseGenerator
from app.ai.conversation.speech_coordinator import SpeechCoordinator
from app.ai.conversation.streaming_manager import StreamingManager


class UniversalConversationEngine(IUniversalConversationEngine):
    """The central Human-Like Conversation & Emotional Intelligence Platform runtime for Nova AI."""

    def __init__(self, config: Optional[ConversationConfiguration] = None) -> None:
        self.config = config or ConversationConfiguration()
        self.manager = ConversationManager()
        self.emotion_engine = EmotionEngine()
        self.personality_engine = PersonalityEngine()
        self.dialog_manager = DialogManager()
        self.state_tracker = ConversationStateTracker()
        self.history_tracker = ConversationHistoryTracker()
        self.memory = ConversationMemory()
        self.context_tracker = CognitiveContextTracker()
        self.adaptive_formatter = AdaptiveResponseFormatter()
        self.response_generator = ResponseGenerator()
        self.compressor = ConversationCompressor()
        self.followup_engine = FollowupEngine()
        self.clarification_engine = ClarificationEngine()
        self.interruption_manager = InterruptionManager()
        self.streaming_manager = StreamingManager()
        self.speech_coordinator = SpeechCoordinator()
        self.human_behavior_engine = HumanBehaviorEngine()
        self.learning_engine = ConversationLearningEngine()
        self.recovery_engine = ConversationRecoveryEngine()
        self.validator = ConversationValidator()

        self.metrics_tracker = ConversationMetricsTracker()
        self.health_monitor = ConversationHealthMonitor()
        self.cache = ConversationCache(ttl_seconds=self.config.cache_ttl_seconds)

    async def conversation(self, prompt: str, session_id: Optional[str] = None, **kwargs: Any) -> ConversationResponsePayload:
        """Executes multi-turn conversation turn."""
        start_time = time.time()
        sess = self.manager.get_session(session_id) if session_id else None
        if not sess:
            sess = self.manager.create_session()
            self.metrics_tracker.record_conversation()

        # 1. Human behavior & emotion detection
        behavior = self.human_behavior_engine.analyze_behavior(prompt)
        emotion = self.emotion_engine.detect_emotion(prompt)

        # 2. Resolve follow-up references
        resolved_prompt = self.followup_engine.resolve_followup(sess, prompt)

        # 3. Add user turn
        user_turn = self.history_tracker.add_turn(sess, ConversationTurnRole.USER, resolved_prompt)
        user_turn.emotion = emotion
        self.memory.remember_turn(sess.session_id, user_turn)
        self.learning_engine.learn_from_turn(resolved_prompt)

        # 4. Personality & context
        personality = self.personality_engine.get_active_profile(sess.session_id)
        ctx = self.context_tracker.capture_snapshot(**kwargs)

        # 5. Process dialog & generate response
        self.dialog_manager.process_utterance(sess.session_id, resolved_prompt)
        raw_resp = await self.response_generator.generate_response(resolved_prompt, emotion, personality)
        formatted_resp = self.adaptive_formatter.format_response(raw_resp, emotion, personality)

        # 6. Add assistant turn
        asst_turn = self.history_tracker.add_turn(sess, ConversationTurnRole.ASSISTANT, formatted_resp)

        # 7. Check if clarification options needed
        clarifications = []
        if "dashboard" in resolved_prompt.lower() and "create" in resolved_prompt.lower():
            clarifications = self.clarification_engine.generate_clarification_options(resolved_prompt, ctx)

        latency = (time.time() - start_time) * 1000.0
        self.metrics_tracker.record_turn(emotion_detected=True, latency_ms=latency)

        return ConversationResponsePayload(
            session_id=sess.session_id,
            text_response=formatted_resp,
            audio_output_path="./data/audio/output_speech.wav",
            emotion=emotion,
            personality=personality,
            latency_ms=latency,
            clarification_options=clarifications,
        )

    async def continue_conversation(self, session_id: str, prompt: str, **kwargs: Any) -> ConversationResponsePayload:
        """Continues active conversation session."""
        return await self.conversation(prompt, session_id=session_id, **kwargs)

    async def conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves turn history list."""
        sess = self.manager.get_session(session_id)
        return self.history_tracker.format_history_list(sess) if sess else []

    async def conversation_summary(self, session_id: str) -> str:
        """Retrieves conversation summary."""
        sess = self.manager.get_session(session_id)
        return self.history_tracker.summarize_history(sess) if sess else "No session found."

    async def conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieves cognitive context snapshot."""
        ctx = self.context_tracker.capture_snapshot()
        return ctx.model_dump(mode="json")

    async def set_personality(self, personality: str, session_id: Optional[str] = None) -> PersonalityMetadata:
        """Sets active personality profile."""
        sess_id = session_id or "global"
        ptype = PersonalityProfileType(personality.lower()) if personality.lower() in [p.value for p in PersonalityProfileType] else PersonalityProfileType.DEVELOPER
        return self.personality_engine.set_active_profile(sess_id, ptype)

    async def current_emotion(self, session_id: str) -> EmotionMetadata:
        """Retrieves last detected emotion."""
        sess = self.manager.get_session(session_id)
        if sess and sess.turns:
            return sess.turns[-1].emotion
        return EmotionMetadata()

    async def interrupt_response(self, session_id: str) -> bool:
        """Triggers barge-in interruption signal for session."""
        handled = self.interruption_manager.handle_interruption(session_id)
        if handled:
            self.metrics_tracker.record_interruption()
        return handled

    async def check_health(self) -> ConversationHealth:
        """Retrieves conversation engine health diagnostics."""
        sessions = self.manager.list_sessions()
        total_turns = sum(len(s.turns) for s in sessions.values())
        return self.health_monitor.check_health(len(sessions), total_turns)

    async def get_metrics(self) -> ConversationMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()
