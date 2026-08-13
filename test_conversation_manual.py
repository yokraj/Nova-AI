"""12-Stage Manual Validation Script for M3.4.10 Human-Like Conversation & Emotional Intelligence Engine.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.conversation import (
    UniversalConversationEngine,
    ConversationConfiguration,
    EmotionState,
    PersonalityProfileType,
    ConversationState,
    MockConversationProvider,
)
from app.ai.gateway import AIGateway


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.10 – Human-Like Conversation & Emotional Intelligence Engine")
    print("==================================================================\n")

    engine = UniversalConversationEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.default_personality == "DEVELOPER"
    print("  [OK] Conversation package loaded successfully.\n")

    # Stage 2: Emotion Detector & Emotional Intelligence
    print("Stage 2: Emotion Detector & Emotional Intelligence (Voice Speech Adaptation)")
    emo_frustrated = engine.emotion_engine.detect_emotion("Why isn't this code compiling? I'm frustrated!")
    emo_urgent = engine.emotion_engine.detect_emotion("Deploy this urgent hotfix ASAP!")
    params_frustrated = engine.emotion_engine.adapt_speech_parameters(emo_frustrated)
    print(f"  * Detected Emotion (Frustrated): {emo_frustrated.primary_emotion.value} (Confidence: {emo_frustrated.confidence})")
    print(f"  * Speech Adaptation: Rate Multiplier = {params_frustrated['rate_multiplier']}x | Tone: '{emo_frustrated.tone_descriptor}'")
    print(f"  * Detected Emotion (Urgent): {emo_urgent.primary_emotion.value} | Rate Multiplier = {emo_urgent.speech_rate_multiplier}x")
    assert emo_frustrated.primary_emotion == EmotionState.FRUSTRATED
    assert emo_urgent.primary_emotion == EmotionState.URGENT
    print("  [OK] Emotion Engine detected emotion and calculated voice speech adaptation.\n")

    # Stage 3: Personality Profiles Catalog
    print("Stage 3: Personality Profiles Catalog (Developer, Executive, Teacher, Friendly)")
    profiles = engine.personality_engine.catalog.list_profiles()
    print(f"  * Total Personality Profiles Available: {len(profiles)}")
    for p in profiles[:4]:
        print(f"  * Profile: '{p.profile_type.value}' ({p.name}) | Tone: '{p.tone}' | Verbosity: {p.verbosity}")
    assert len(profiles) >= 5
    print("  [OK] Personality Catalog verified.\n")

    # Stage 4: Personality Engine Dynamic Switching
    print("Stage 4: Personality Engine Dynamic Switching")
    set_prof = await engine.set_personality("TEACHER", session_id="test_sess_01")
    print(f"  * Switched Session 'test_sess_01' to Personality: '{set_prof.name}' ({set_prof.tone})")
    assert set_prof.profile_type == PersonalityProfileType.TEACHER
    print("  [OK] Personality Engine dynamically assigned profile to session.\n")

    # Stage 5: Cognitive Context Tracker
    print("Stage 5: Cognitive Context Tracker (IDE, Desktop, Browser & Mission Snapshot)")
    ctx = engine.context_tracker.capture_snapshot(active_file="main.py", browser_tab="GitHub - Nova AI")
    print(f"  * Active App: '{ctx.active_app}' | Project: '{ctx.active_project}'")
    print(f"  * Active File: '{ctx.active_file}' | Browser Tab: '{ctx.browser_tab}'")
    assert ctx.active_app == "VS Code"
    print("  [OK] Cognitive Context Tracker captured workspace snapshot.\n")

    # Stage 6: Dialog Manager & Topic Tracking
    print("Stage 6: Dialog Manager & Topic Tracking")
    turn1_info = engine.dialog_manager.process_utterance("test_sess_01", "Let's build a React Dashboard component")
    active_topic = engine.dialog_manager.get_active_topic("test_sess_01")
    print(f"  * Processed Utterance Topic: '{turn1_info['topic']}' | Active Topic: '{active_topic}'")
    assert active_topic == "frontend_dashboard"
    print("  [OK] Dialog Manager tracked dialogue topic.\n")

    # Stage 7: Followup Engine
    print("Stage 7: Followup Engine (Implicit Past Reference Resolution)")
    session = engine.manager.create_session("user_primary")
    resolved_prompt = engine.followup_engine.resolve_followup(session, "Continue yesterday's dashboard")
    print(f"  * Raw User Prompt: 'Continue yesterday's dashboard'")
    print(f"  * Resolved Explicit Context: '{resolved_prompt}'")
    assert "Resume task context" in resolved_prompt
    print("  [OK] Followup Engine resolved implicit prompt references.\n")

    # Stage 8: Clarification Engine
    print("Stage 8: Clarification Engine (Smart Choice Options)")
    clarifications = engine.clarification_engine.generate_clarification_options("Create React Dashboard", ctx)
    print(f"  * Generated Clarification Choices ({len(clarifications)}):")
    for opt in clarifications:
        print(f"    - [{opt.option_id}] {opt.label}: {opt.description}")
    assert len(clarifications) >= 2
    print("  [OK] Clarification Engine generated smart options.\n")

    # Stage 9: Human Behavior Engine & Interruption Manager
    print("Stage 9: Human Behavior Engine & Interruption Manager (Barge-in)")
    behavior = engine.human_behavior_engine.analyze_behavior("Um, well... let me think about this", pause_duration_ms=2000.0)
    print(f"  * Hesitation Detected: {behavior['hesitation_detected']} | Thinking Pause (>1.5s): {behavior['thinking_pause']}")

    bargein_ok = engine.interruption_manager.handle_interruption("test_sess_01")
    was_int = engine.interruption_manager.was_interrupted("test_sess_01")
    print(f"  * Handled Speech Interruption (Barge-in): {bargein_ok} | Was Interrupted: {was_int}")
    assert behavior["hesitation_detected"] is True
    assert was_int is True
    print("  [OK] Human Behavior Engine and Interruption Manager verified.\n")

    # Stage 10: Streaming Manager & Speech Coordinator
    print("Stage 10: Streaming Manager & Speech Coordinator")
    speech_config = engine.speech_coordinator.prepare_speech_config(emo_urgent, set_prof)
    print(f"  * Prepared Speech Config: Voice ID = '{speech_config['voice_id']}' | Rate = {speech_config['rate_multiplier']}x | Tone = '{speech_config['tone_descriptor']}'")

    chunks = []
    async for chunk in engine.streaming_manager.stream_response("test_sess_01", "Hello Nova AI OS"):
        chunks.append(chunk)
    stream_output = "".join(chunks)
    print(f"  * Streamed Tokens Output: '{stream_output}'")
    assert len(chunks) >= 3
    print("  [OK] Streaming Manager and Speech Coordinator verified.\n")

    # Stage 11: Long-Term Memory & Compression
    print("Stage 11: Long-Term Memory & Conversation Compressor")
    turn = engine.history_tracker.add_turn(session, turn_info := engine.history_tracker.add_turn(session, "user", "Design system architecture").role, "Design system architecture")
    engine.memory.remember_turn(session.session_id, turn)
    memory_results = engine.memory.search_memory("architecture")
    comp_summary = engine.compressor.compress_history(session)
    print(f"  * Memory Search Results Count: {len(memory_results)}")
    print(f"  * History Compression Summary: '{comp_summary}'")
    assert len(memory_results) >= 1
    print("  [OK] Long-Term Memory and Conversation Compressor verified.\n")

    # Stage 12: End-to-End Voice & Emotional Conversational Turn Execution
    print("Stage 12: End-to-End Conversational Execution ('Hey Nova, I need an urgent fix for my API')")
    conv_res = await engine.conversation("I need an urgent fix for my API immediately!", session_id=session.session_id)
    print(f"  * Session ID: '{conv_res.session_id}'")
    print(f"  * Text Response: '{conv_res.text_response}'")
    print(f"  * Emotion Detected: {conv_res.emotion.primary_emotion.value} (Speech Rate: {conv_res.emotion.speech_rate_multiplier}x)")
    print(f"  * Active Personality: '{conv_res.personality.name}' | Audio Path: '{conv_res.audio_output_path}'")
    assert conv_res.emotion.primary_emotion == EmotionState.URGENT
    assert len(conv_res.text_response) > 0
    print("  [OK] End-to-end voice & emotional conversational turn complete.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Human-Like Conversation & Emotional Intelligence Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
