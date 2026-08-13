"""Unit and integration tests for M3.4.19 AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine.
"""

import pytest
from app.ai.os_runtime.engine import NovaOperatingSystemEngine
from app.ai.os_runtime.manager import OSRuntimeManagerFacade
from app.ai.os_runtime.models import OSState, VADState, VoiceUserRole
from app.ai.os_runtime.wake_word_engine import WakeWordEngine
from app.ai.os_runtime.voice_activity_detector import VoiceActivityDetector
from app.ai.os_runtime.streaming_stt import StreamingSpeechRecognition
from app.ai.os_runtime.voice_authenticator import VoiceAuthenticator
from app.ai.os_runtime.streaming_conversation_engine import StreamingConversationEngine
from app.ai.os_runtime.interruption_engine import InterruptionEngine
from app.ai.os_runtime.voice_session_manager import VoiceSessionManager
from app.ai.os_runtime.context_awareness_engine import ContextAwarenessEngine
from app.ai.os_runtime.confirmation_engine import ConfirmationEngine
from app.ai.os_runtime.voice_notification_engine import VoiceNotificationEngine
from app.ai.os_runtime.hands_free_computing import HandsFreeComputingEngine
from app.ai.os_runtime.voice_agent_workforce import VoiceAgentWorkforce
from app.ai.os_runtime.background_mission_support import BackgroundMissionSupport
from app.ai.os_runtime.system_tray_runtime import SystemTrayRuntime
from app.ai.os_runtime.voice_observability import VoiceObservabilityMetrics


@pytest.mark.anyio
async def test_wake_word_and_vad():
    wake = WakeWordEngine(primary_phrase="Hey Nova")
    detection = await wake.process_audio_chunk(b"sample_audio_stream_data_buffer_content")
    assert detection.detected is True
    assert detection.phrase == "Hey Nova"

    vad = VoiceActivityDetector()
    state = vad.detect_vad(b"speech_sample_buffer_over_512_bytes_" * 20)
    assert state == VADState.SPEECH_IN_PROGRESS


@pytest.mark.anyio
async def test_streaming_stt_and_voice_auth():
    stt = StreamingSpeechRecognition()
    transcripts = []
    async for item in stt.transcribe_stream(None):
        transcripts.append(item)
    assert len(transcripts) >= 4
    assert transcripts[-1].is_final is True

    auth = VoiceAuthenticator(owner_voice_id="owner_primary")
    res = await auth.verify_speaker(b"biometric_voice_print_sample")
    assert res.verified is True
    assert res.role == VoiceUserRole.OWNER


@pytest.mark.anyio
async def test_early_reasoning_and_barge_in_interrupt():
    conv_engine = StreamingConversationEngine()
    early_res = await conv_engine.evaluate_partial("Hey Nova, open VS Code")
    assert "Visual Studio Code" in early_res.speculative_action

    interrupt = InterruptionEngine()
    interrupt.set_speaking_state(True)
    stopped = await interrupt.handle_barge_in()
    assert stopped is True
    assert interrupt.tts_speaking is False


@pytest.mark.anyio
async def test_context_awareness_and_session_manager():
    ctx_engine = ContextAwarenessEngine()
    ctx = ctx_engine.capture_context()
    assert ctx["foreground_app"] == "Visual Studio Code"
    assert "github.com" in ctx["current_browser_url"]

    session = VoiceSessionManager()
    session.record_turn("user", "Hey Nova")
    snap = session.get_context_snapshot()
    assert snap["history_turns_count"] == 1


@pytest.mark.anyio
async def test_confirmation_engine_and_notifications():
    confirm = ConfirmationEngine()
    hold = await confirm.request_confirmation("delete_file", "Delete old build directory")
    assert hold.confirmed is False

    ok = await confirm.approve_confirmation(hold.hold_id)
    assert ok is True

    notif_engine = VoiceNotificationEngine()
    notif = await notif_engine.notify_voice("Mission Complete", "Financial report mission finished.")
    assert notif.spoken is True


@pytest.mark.anyio
async def test_hands_free_macro_and_15_voice_agents():
    hands_free = HandsFreeComputingEngine()
    res = await hands_free.execute_voice_macro("Hey Nova, open VS Code, run backend, push to GitHub")
    assert res["status"] == "completed"
    assert len(res["executed_steps"]) >= 3

    workforce = VoiceAgentWorkforce()
    agents = workforce.list_agents()
    assert len(agents) == 15


@pytest.mark.anyio
async def test_background_missions_and_system_tray():
    missions = BackgroundMissionSupport()
    cp = await missions.create_checkpoint("msn_01", "Data Scraping Mission", 45.0, "Step 3")
    assert cp.progress_percent == 45.0

    restored = await missions.recover_missions_after_reboot()
    assert len(restored) >= 1

    tray = SystemTrayRuntime()
    status = tray.get_tray_status()
    assert status.listening_active is True


@pytest.mark.anyio
async def test_nova_operating_system_engine_master_facade():
    engine = NovaOperatingSystemEngine()
    booted = await engine.boot_system()
    assert booted is True

    turn_res = await engine.process_voice_turn(b"audio_stream_data_buffer_sample")
    assert turn_res["wake_word"]["detected"] is True
    assert turn_res["os_state"] == OSState.RUNNING.value

    health = engine.get_os_health()
    assert health.is_healthy is True
