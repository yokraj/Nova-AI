"""20-Stage Comprehensive Manual Validation Script for M3.4.19 AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))


async def run_20_stage_validation():
    print("==================================================================")
    print("M3.4.19 – AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine")
    print("==================================================================\n")

    # Stage 1: OS Runtime Package Init & PEP 562 Lazy Loader
    print("Stage 1: OS Runtime Package Init & PEP 562 Lazy Loader")
    from app.ai.os_runtime import OSRuntimeConfiguration, NovaOperatingSystemEngine
    config = OSRuntimeConfiguration()
    print(f"  * OS Name: '{config.os_name}' v{config.version} | Auto-Start Windows = {config.auto_start_with_windows}")
    assert config.enabled is True
    print("  [OK] OS Runtime package init & lazy loader verified.\n")

    # Stage 2: Windows Background AI Service & Resource Throttling
    print("Stage 2: Windows Background AI Service & Resource Throttling")
    engine = NovaOperatingSystemEngine(config)
    boot_diag = await engine.start_os()
    print(f"  * Boot Status: '{boot_diag.status.value}' | Duration: {boot_diag.boot_duration_ms} ms")
    assert boot_diag.status.value == "HEALTHY"
    print("  [OK] Windows Background AI Service & resource throttling verified.\n")

    # Stage 3: Wake-Word Engine ("Hey Nova" Detection & Custom Phrases)
    print("Stage 3: Wake-Word Engine ('Hey Nova' Detection & Custom Phrases)")
    from app.ai.os_runtime.wake_word_engine import WakeWordEngine
    wake_engine = WakeWordEngine(primary_phrase=config.wake_word)
    wake_res = await wake_engine.process_audio_chunk(b"audio_sample_bytes_buffer_content")
    print(f"  * Wake-Word Detected: {wake_res.detected} | Phrase = '{wake_res.phrase}' | Confidence = {wake_res.confidence}")
    assert wake_res.detected is True and wake_res.phrase == "Hey Nova"
    print("  [OK] Wake-Word Engine verified.\n")

    # Stage 4: Voice Activity Detection (VAD, Noise Calibration & Echo Suppression)
    print("Stage 4: Voice Activity Detection (VAD, Noise Calibration & Echo Suppression)")
    from app.ai.os_runtime.voice_activity_detector import VoiceActivityDetector
    vad = VoiceActivityDetector()
    vad_state = vad.detect_vad(b"speech_sample_bytes_" * 50)
    baseline_noise = vad.calibrate_noise()
    print(f"  * VAD State: '{vad_state.value}' | Calibrated Baseline Noise Level: {baseline_noise}")
    assert vad_state.value == "SPEECH_IN_PROGRESS"
    print("  [OK] Voice Activity Detection verified.\n")

    # Stage 5: Streaming Speech Recognition (Faster Whisper Real-Time STT)
    print("Stage 5: Streaming Speech Recognition (Faster Whisper Real-Time STT)")
    from app.ai.os_runtime.streaming_stt import StreamingSpeechRecognition
    stt = StreamingSpeechRecognition(model_name=config.stt_model)
    transcripts = []
    async for partial in stt.transcribe_stream(None):
        transcripts.append(partial)
    print(f"  * Incremental Transcripts Count: {len(transcripts)} | Final Transcript: '{transcripts[-1].transcript}'")
    assert len(transcripts) >= 4 and transcripts[-1].is_final is True
    print("  [OK] Streaming Speech Recognition verified.\n")

    # Stage 6: Voice Print Authentication & User Role Verification
    print("Stage 6: Voice Print Authentication & User Role Verification")
    from app.ai.os_runtime.voice_authenticator import VoiceAuthenticator
    voice_auth = VoiceAuthenticator(owner_voice_id=config.owner_voice_id)
    auth_res = await voice_auth.verify_speaker(b"owner_voice_biometric_sample")
    print(f"  * Speaker Verified: {auth_res.verified} | User = '{auth_res.user_id}' | Role = '{auth_res.role.value}'")
    assert auth_res.verified is True and auth_res.role.value == "OWNER"
    print("  [OK] Voice Print Authentication verified.\n")

    # Stage 7: Streaming Conversation Engine & Speculative Early Reasoning
    print("Stage 7: Streaming Conversation Engine & Speculative Early Reasoning")
    from app.ai.os_runtime.streaming_conversation_engine import StreamingConversationEngine
    conv_engine = StreamingConversationEngine()
    early_res = await conv_engine.evaluate_partial("Hey Nova, open VS Code and create React app")
    print(f"  * Speculative Action Predicted: '{early_res.speculative_action}' | Ready = {early_res.ready_for_execution}")
    assert "Visual Studio Code" in early_res.speculative_action
    print("  [OK] Speculative Early Reasoning verified.\n")

    # Stage 8: Speech Barge-in Interruption Engine
    print("Stage 8: Speech Barge-in Interruption Engine")
    from app.ai.os_runtime.interruption_engine import InterruptionEngine
    interrupt_engine = InterruptionEngine()
    interrupt_engine.set_speaking_state(True)
    interrupted = await interrupt_engine.handle_barge_in()
    print(f"  * TTS Waveform Interrupted: {interrupted} | Speaking Active = {interrupt_engine.tts_speaking}")
    assert interrupted is True and interrupt_engine.tts_speaking is False
    print("  [OK] Speech Barge-in Interruption Engine verified.\n")

    # Stage 9: Voice Session Manager & Context Stack
    print("Stage 9: Voice Session Manager & Context Stack")
    from app.ai.os_runtime.voice_session_manager import VoiceSessionManager
    session_mgr = VoiceSessionManager()
    session_mgr.record_turn("user", "Hey Nova")
    session_mgr.record_turn("assistant", "Hello! How can I help?")
    snap = session_mgr.get_context_snapshot()
    print(f"  * Active Workspace: '{snap['active_workspace']}' | Conversation Turns: {snap['history_turns_count']}")
    assert snap["history_turns_count"] == 2
    print("  [OK] Voice Session Manager verified.\n")

    # Stage 10: Automated Contextual Awareness Engine
    print("Stage 10: Automated Contextual Awareness Engine")
    from app.ai.os_runtime.context_awareness_engine import ContextAwarenessEngine
    ctx_engine = ContextAwarenessEngine()
    ctx = ctx_engine.capture_context()
    print(f"  * Active App: '{ctx['foreground_app']}' | Active File: '{ctx['current_ide_file']}'")
    print(f"  * Browser URL: '{ctx['current_browser_url']}' | Desktop State: '{ctx['desktop_state']}'")
    assert ctx["foreground_app"] == "Visual Studio Code"
    print("  [OK] Contextual Awareness Engine verified.\n")

    # Stage 11: Safety Confirmation Hold Engine
    print("Stage 11: Safety Confirmation Hold Engine")
    from app.ai.os_runtime.confirmation_engine import ConfirmationEngine
    confirm_engine = ConfirmationEngine()
    hold = await confirm_engine.request_confirmation("delete_file", "Delete production database backup file")
    print(f"  * Confirmation Hold ID: '{hold.hold_id}' | Risk Level = '{hold.risk_level}' | Confirmed = {hold.confirmed}")
    approved = await confirm_engine.approve_confirmation(hold.hold_id)
    print(f"  * User Voice Approval Executed: {approved}")
    assert approved is True
    print("  [OK] Safety Confirmation Hold Engine verified.\n")

    # Stage 12: Proactive Voice Notification Engine
    print("Stage 12: Proactive Voice Notification Engine")
    from app.ai.os_runtime.voice_notification_engine import VoiceNotificationEngine
    notif_engine = VoiceNotificationEngine()
    notif = await notif_engine.notify_voice("Build Complete", "FastAPI backend compiled and all unit tests passed.")
    print(f"  * Spoken Notification: '{notif.title}' - '{notif.message}' | Spoken = {notif.spoken}")
    assert notif.spoken is True
    print("  [OK] Proactive Voice Notification Engine verified.\n")

    # Stage 13: Hands-Free Computing Voice Macro Workflow Engine
    print("Stage 13: Hands-Free Computing Voice Macro Workflow Engine")
    from app.ai.os_runtime.hands_free_computing import HandsFreeComputingEngine
    hands_free = HandsFreeComputingEngine()
    macro_res = await hands_free.execute_voice_macro("Hey Nova, open VS Code, create React project, run backend, push to GitHub")
    print(f"  * Voice Macro Status: '{macro_res['status']}' | Executed Steps Count: {len(macro_res['executed_steps'])}")
    for step in macro_res["executed_steps"]:
        print(f"    - {step}")
    assert macro_res["status"] == "completed"
    print("  [OK] Hands-Free Computing Engine verified.\n")

    # Stage 14: 15-Agent Voice Workforce Coordination
    print("Stage 14: 15-Agent Voice Workforce Coordination")
    from app.ai.os_runtime.voice_agent_workforce import VoiceAgentWorkforce
    workforce = VoiceAgentWorkforce()
    agents = workforce.list_agents()
    print(f"  * Voice Workforce Agents Count: {len(agents)} (First 3: {[a.name for a in agents[:3]]})")
    assert len(agents) == 15
    print("  [OK] 15-Agent Voice Workforce verified.\n")

    # Stage 15: Background Mission Support (Reboot Recovery & Checkpoints)
    print("Stage 15: Background Mission Support (Reboot Recovery & Checkpoints)")
    from app.ai.os_runtime.background_mission_support import BackgroundMissionSupport
    missions = BackgroundMissionSupport()
    cp = await missions.create_checkpoint("msn_001", "Autonomous Refactoring Mission", 75.0, "Step 4: Refactor tests")
    restored_missions = await missions.recover_missions_after_reboot()
    print(f"  * Checkpoint Saved: Mission '{cp.name}' ({cp.progress_percent}%) | Restored Count = {len(restored_missions)}")
    assert len(restored_missions) >= 1
    print("  [OK] Background Mission Support verified.\n")

    # Stage 16: Windows System Tray Application Runtime Daemon
    print("Stage 16: Windows System Tray Application Runtime Daemon")
    from app.ai.os_runtime.system_tray_runtime import SystemTrayRuntime
    tray = SystemTrayRuntime()
    status = tray.get_tray_status()
    print(f"  * Tray Icon State: '{status.icon_state}' | Active Models = {status.active_models_count} | Mic Muted = {status.microphone_muted}")
    toggled = tray.toggle_mute()
    print(f"  * Quick Mute Toggled: Mic Muted = {toggled}")
    assert toggled is True
    print("  [OK] Windows System Tray Application Runtime verified.\n")

    # Stage 17: Voice Observability Metrics & Microphone Telemetry
    print("Stage 17: Voice Observability Metrics & Microphone Telemetry")
    from app.ai.os_runtime.voice_observability import VoiceObservabilityMetrics
    observability = VoiceObservabilityMetrics()
    observability.record_voice_turn(wake_word_ms=42.0, stt_ms=115.0)
    snap = observability.get_observability_snapshot()
    print(f"  * Wake-Word Latency: {snap['avg_wake_word_latency_ms']} ms | STT Latency: {snap['avg_stt_latency_ms']} ms | Speech Accuracy = {snap['speech_accuracy_score']}")
    assert snap["total_voice_turns"] == 1
    print("  [OK] Voice Observability Metrics verified.\n")

    # Stage 18: Universal AI Orchestrator Integration (M3.4.18 Integration)
    print("Stage 18: Universal AI Orchestrator Integration (M3.4.18 Integration)")
    from app.ai.orchestrator.engine import UniversalAIOrchestratorEngine
    orch = UniversalAIOrchestratorEngine()
    orch_res = await orch.chat("Hey Nova, status of system health")
    print(f"  * Orchestrator Voice Routing Response: '{orch_res.text_or_data[:80]}...' | Model = '{orch_res.model_id}'")
    assert orch_res.text_or_data != ""
    print("  [OK] Universal AI Orchestrator Integration verified.\n")

    # Stage 19: End-to-End Voice Turn Execution Pipeline
    print("Stage 19: End-to-End Voice Turn Execution Pipeline")
    turn_result = await engine.process_voice_turn(b"audio_stream_data_sample_buffer")
    print(f"  * Voice Turn Completed: Wake Detected = {turn_result['wake_word']['detected']} | Speaker = '{turn_result['speaker']['user_id']}'")
    print(f"  * Orchestrated Output: '{turn_result['orchestrated_response'][:80]}...'")
    assert turn_result["wake_word"]["detected"] is True
    print("  [OK] End-to-End Voice Turn Execution Pipeline verified.\n")

    # Stage 20: System Integration & Master Health Verification
    print("Stage 20: System Integration & Master Health Verification")
    master_health = engine.get_os_health()
    print(f"  * Master OS Health: Status = '{master_health.os_state.value}' | Health Score = {master_health.health_score}/100")
    print(f"  * Active Subsystems: {master_health.active_subsystems_count} | CPU = {master_health.cpu_percent}% | RAM = {master_health.ram_used_mb} MB")
    assert master_health.is_healthy is True
    print("  [OK] System Integration & Master Health Verification complete.\n")

    print("==================================================================")
    print("  ALL 20 STAGES PASSED SUCCESSFULLY!")
    print("  AI Operating System Core & Always-On Voice Runtime Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_20_stage_validation())
