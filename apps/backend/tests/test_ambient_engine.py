"""Unit tests for Ambient Intelligence & Continuous Voice Assistant."""

import pytest
from app.ai.ambient.ambient_engine import AmbientEngine
from app.ai.ambient.ambient_manager import AmbientManager
from app.ai.ambient.configuration import AmbientConfiguration
from app.ai.ambient.context_pipeline import ContextPipeline
from app.ai.ambient.conversation_manager import ConversationManager
from app.ai.ambient.microphone_listener import MicrophoneListener
from app.ai.ambient.models import AmbientState, AudioFrame
from app.ai.ambient.proactive_assistant import ProactiveAssistant
from app.ai.ambient.wake_word_runtime import WakeWordRuntime
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.mark.anyio
async def test_ambient_configuration():
    """Verifies default ambient configuration settings."""
    config = AmbientConfiguration()
    assert config.enabled is True
    assert config.microphone_enabled is True
    assert "Hey Nova" in config.wake_words


@pytest.mark.anyio
async def test_microphone_listener():
    """Verifies continuous microphone listener lifecycle and privacy pause/resume."""
    listener = MicrophoneListener()
    await listener.start_listening()
    assert listener.is_active is True

    await listener.pause_listening()
    assert listener.is_paused is True

    await listener.resume_listening()
    assert listener.is_paused is False

    await listener.stop_listening()
    assert listener.is_active is False


@pytest.mark.anyio
async def test_wake_word_runtime():
    """Verifies wake word phrase detection and text matching."""
    ww = WakeWordRuntime()
    frame = AudioFrame(data_bytes=b"\x00" * 320, has_speech=True)
    match = await ww.process_frame(frame)
    assert match is not None
    assert match.phrase == "Hey Nova"

    text_match = await ww.detect_in_text("Hey Nova, what time is it?")
    assert text_match is not None
    assert text_match.phrase == "Hey Nova"


@pytest.mark.anyio
async def test_conversation_manager():
    """Verifies multi-turn voice conversation turn handling."""
    cm = ConversationManager()
    res = await cm.handle_user_speech("You're in a Teams meeting. Summarize agenda.")
    assert "Summarizing Microsoft Teams" in res["response"]
    assert res["turns_count"] == 2


@pytest.mark.anyio
async def test_desktop_context_pipeline():
    """Verifies desktop window, clipboard, and notification context aggregation."""
    cp = ContextPipeline()
    snapshot = await cp.get_composite_snapshot()
    assert snapshot.active_window.process_name == "Code.exe"
    assert snapshot.clipboard.is_error_log is True
    assert snapshot.is_in_meeting is True


@pytest.mark.anyio
async def test_proactive_assistant():
    """Verifies proactive suggestions generation across categories."""
    cp = ContextPipeline()
    snapshot = await cp.get_composite_snapshot()
    pa = ProactiveAssistant()
    suggestions = await pa.evaluate_context(snapshot)
    assert len(suggestions) >= 4
    categories = [s.category for s in suggestions]
    assert "meeting" in categories
    assert "debugging" in categories


@pytest.mark.anyio
async def test_ambient_engine_lifecycle_and_privacy():
    """Verifies AmbientEngine lifecycle and privacy mode toggles."""
    engine = AmbientEngine()
    await engine.start()
    assert engine.state == AmbientState.LISTENING

    await engine.pause_listening()
    assert engine.state == AmbientState.PAUSED

    await engine.resume_listening()
    assert engine.state == AmbientState.LISTENING

    await engine.stop()
    assert engine.state == AmbientState.IDLE


@pytest.mark.anyio
async def test_ambient_proactive_alerts():
    """Verifies proactive alerts retrieval and telemetry metrics."""
    engine = AmbientEngine()
    alerts = await engine.get_proactive_alerts()
    assert len(alerts) >= 1
    metrics = await engine.get_metrics()
    assert metrics.proactive_suggestions_issued >= 1


@pytest.mark.anyio
async def test_gateway_ambient_apis():
    """Verifies AI Gateway ambient methods."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    start_res = await gateway.start_ambient()
    assert start_res["status"] == "started"

    status_res = await gateway.ambient_status()
    assert status_res["status"] == "healthy"

    conv_res = await gateway.conversation("Hey Nova, summarize Teams meeting")
    assert "response" in conv_res

    stop_res = await gateway.stop_ambient()
    assert stop_res["status"] == "stopped"
