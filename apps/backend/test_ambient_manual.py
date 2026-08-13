"""12-Stage Manual Validation Script for M3.3.14 Ambient Intelligence & Continuous Voice Assistant."""

import asyncio
import sys
import structlog

from app.ai.ambient.active_window_monitor import ActiveWindowMonitor
from app.ai.ambient.ambient_engine import AmbientEngine
from app.ai.ambient.ambient_manager import AmbientManager
from app.ai.ambient.clipboard_monitor import ClipboardMonitor
from app.ai.ambient.configuration import AmbientConfiguration
from app.ai.ambient.context_pipeline import ContextPipeline
from app.ai.ambient.conversation_manager import ConversationManager
from app.ai.ambient.idle_detector import IdleDetector
from app.ai.ambient.microphone_listener import MicrophoneListener
from app.ai.ambient.models import AmbientState, AudioFrame
from app.ai.ambient.proactive_assistant import ProactiveAssistant
from app.ai.ambient.wake_word_runtime import WakeWordRuntime
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve

logger = structlog.get_logger("test_ambient_manual")


async def run_manual_validation() -> None:
    print("=========================================")
    print("Nova AI Ambient Intelligence Engine Validation")
    print("=========================================")

    # Stage 1: Configuration & Settings
    config = AmbientConfiguration()
    assert config.enabled is True
    assert config.microphone_enabled is True
    print("Stage 1  Ambient Configuration     PASS")

    # Stage 2: Microphone Listener Lifecycle
    mic = MicrophoneListener()
    await mic.start_listening()
    await mic.pause_listening()
    await mic.resume_listening()
    await mic.stop_listening()
    print("Stage 2  Microphone Listener Stream PASS")

    # Stage 3: Wake Word Detection Engine
    ww = WakeWordRuntime()
    frame = AudioFrame(has_speech=True)
    match = await ww.process_frame(frame)
    assert match is not None
    assert match.phrase == "Hey Nova"
    print("Stage 3  Wake Word Detection Engine PASS")

    # Stage 4: Multi-Turn Conversation Pipeline
    cm = ConversationManager()
    res = await cm.handle_user_speech("You're in a Teams meeting. Summarize agenda.")
    assert "Summarizing Microsoft Teams" in res["response"]
    print("Stage 4  Multi-Turn Voice Pipeline  PASS")

    # Stage 5: Active Window & Desktop Monitor
    aw = ActiveWindowMonitor()
    win = await aw.get_active_window()
    assert win.process_name == "Code.exe"
    print("Stage 5  Active Window & App Monitor PASS")

    # Stage 6: Clipboard Error & Code Monitor
    cb = ClipboardMonitor()
    clip = await cb.get_clipboard_snapshot()
    assert clip.is_error_log is True
    print("Stage 6  Clipboard & Stacktrace     PASS")

    # Stage 7: Context Pipeline Aggregator
    cp = ContextPipeline()
    snap = await cp.get_composite_snapshot()
    assert snap.is_in_meeting is True
    print("Stage 7  Context Pipeline           PASS")

    # Stage 8: Proactive Suggestions Engine
    pa = ProactiveAssistant()
    sugs = await pa.evaluate_context(snap)
    assert len(sugs) >= 4
    print("Stage 8  Proactive Suggestions      PASS")

    # Stage 9: Privacy Mode & Controls
    p_config = AmbientConfiguration(privacy_mode=True)
    p_engine = AmbientEngine(config=p_config)
    await p_engine.start()
    assert p_engine.state == AmbientState.PRIVACY_MODE
    print("Stage 9  Privacy Mode Controls      PASS")

    # Stage 10: End-to-End Ambient Engine
    engine = AmbientEngine()
    await engine.start()
    assert engine.state == AmbientState.LISTENING
    conv = await engine.process_conversation("Analyze error log in clipboard")
    assert "response" in conv
    await engine.stop()
    print("Stage 10 End-to-End Ambient Engine  PASS")

    # Stage 11: Ambient Manager Orchestration
    mgr = AmbientManager()
    m_sugs = await mgr.get_proactive_suggestions()
    assert len(m_sugs) >= 1
    print("Stage 11 Ambient Manager Facade    PASS")

    # Stage 12: Gateway Integration
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    g_start = await gateway.start_ambient()
    assert g_start["status"] == "started"
    g_conv = await gateway.conversation("Hey Nova, plan day")
    assert "response" in g_conv
    g_stop = await gateway.stop_ambient()
    assert g_stop["status"] == "stopped"
    print("Stage 12 Gateway Integration        PASS")

    print("\n12/12 PASS")
    print("\nAmbient Intelligence Engine Healthy")


if __name__ == "__main__":
    asyncio.run(run_manual_validation())
