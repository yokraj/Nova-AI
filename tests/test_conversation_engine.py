"""Unit and integration tests for Human-Like Conversation & Emotional Intelligence Engine.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.conversation.conversation_engine import UniversalConversationEngine
from app.ai.conversation.mock_provider import MockConversationProvider
from app.ai.conversation.models import (
    EmotionState,
    PersonalityProfileType,
)


@pytest.mark.anyio
async def test_emotion_detection_and_adaptation():
    engine = UniversalConversationEngine()
    emo_frustrated = engine.emotion_engine.detect_emotion("Why isn't this code compiling? I'm so frustrated!")
    assert emo_frustrated.primary_emotion == EmotionState.FRUSTRATED
    assert emo_frustrated.speech_rate_multiplier < 1.0

    emo_urgent = engine.emotion_engine.detect_emotion("Deploy this urgent fix immediately ASAP")
    assert emo_urgent.primary_emotion == EmotionState.URGENT
    assert emo_urgent.speech_rate_multiplier > 1.0


@pytest.mark.anyio
async def test_personality_profiles():
    engine = UniversalConversationEngine()
    prof_dev = engine.personality_engine.get_profile(PersonalityProfileType.DEVELOPER)
    assert prof_dev.profile_type == PersonalityProfileType.DEVELOPER
    assert "technical" in prof_dev.tone

    prof_exec = engine.personality_engine.get_profile(PersonalityProfileType.EXECUTIVE)
    assert prof_exec.verbosity == "minimal"


@pytest.mark.anyio
async def test_multi_turn_conversation_execution():
    engine = UniversalConversationEngine()
    res1 = await engine.conversation("Create a new React Dashboard component")
    assert res1.session_id is not None
    assert len(res1.text_response) > 0

    res2 = await engine.continue_conversation(res1.session_id, "Add a line chart to yesterday's dashboard")
    assert res2.session_id == res1.session_id
    assert len(res2.text_response) > 0


@pytest.mark.anyio
async def test_conversation_history_and_summary():
    engine = UniversalConversationEngine()
    res = await engine.conversation("Design microservices backend architecture")

    history = await engine.conversation_history(res.session_id)
    assert len(history) >= 2

    summary = await engine.conversation_summary(res.session_id)
    assert "turns" in summary.lower() or "microservices" in summary.lower()


@pytest.mark.anyio
async def test_clarification_engine():
    engine = UniversalConversationEngine()
    res = await engine.conversation("Create React Dashboard")
    assert len(res.clarification_options) >= 1
    assert "Dashboard" in res.clarification_options[0].label


@pytest.mark.anyio
async def test_interruption_barge_in():
    engine = UniversalConversationEngine()
    res = await engine.conversation("Hello Nova, start long voice output")

    interrupted = await engine.interrupt_response(res.session_id)
    assert interrupted is True
    was_int = engine.interruption_manager.was_interrupted(res.session_id)
    assert was_int is True


@pytest.mark.anyio
async def test_speech_coordinator_and_streaming():
    engine = UniversalConversationEngine()
    emo = engine.emotion_engine.detect_emotion("Excited about the launch!")
    prof = engine.personality_engine.get_profile(PersonalityProfileType.FRIENDLY)

    params = engine.speech_coordinator.prepare_speech_config(emo, prof)
    assert params["voice_id"] == "piper_en_friendly"

    chunks = []
    async for chunk in engine.streaming_manager.stream_response("sess_stream", "Test streaming response"):
        chunks.append(chunk)
    assert len(chunks) >= 3


@pytest.mark.anyio
async def test_conversation_health_and_metrics():
    engine = UniversalConversationEngine()
    await engine.conversation("Test turn for metrics")

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_turns_processed >= 2

    metrics = await engine.get_metrics()
    assert metrics.total_turns >= 1


@pytest.mark.anyio
async def test_mock_conversation_provider():
    mock = MockConversationProvider()
    res = await mock.mock_conversation("Test prompt", session_id="mock_001")
    assert res.session_id == "mock_001"
    assert "[Mock Conversation Response]" in res.text_response
