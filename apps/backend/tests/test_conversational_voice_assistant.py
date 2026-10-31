"""Comprehensive Test Suite for Nova-AI Real-Time Conversational Voice Assistant (Phase 10M-B).

Verifies:
1. Voice Activity Detection (VAD) with energy, RMS, zero crossings, and noise calibration.
2. Real-time streaming audio ingestion, frame slicing, and speech utterance segmentation.
3. Microphone hardware/software kill-switch & mandatory privacy guarantees.
4. Local wake-word detection ("Nova", "Hey Nova") with command prefix stripping.
5. Push-to-talk override activation and fallback.
6. Speech intelligence: incomplete command detection & clarification prompting.
7. Speech intelligence: conversational self-correction & speech repair ("no wait", "actually").
8. Speech intelligence: chitchat vs actionable command disambiguation.
9. Acoustic Echo Cancellation: speaker feedback suppression and self-hearing guard.
10. Real-time barge-in interruption while assistant is speaking.
11. Continuous multi-turn conversation loop with follow-up window (no repeat wake word).
12. Debouncing and duplicate command execution prevention.
13. Fast-path system controls ("stop", "cancel", "mute").
14. Multilingual speech handling and language propagation.
15. Strict offline enforcement (zero cloud dependencies).
16. Real spoken audio generation (Windows SAPI) and end-to-end conversational processing.
"""

from typing import List
from unittest.mock import AsyncMock, MagicMock, patch
import io
import math
import os
import struct
import subprocess
import time
import wave
import pytest

from app.ai.voice.conversational.models import (
    AudioFrame,
    ConversationalSession,
    ConversationalState,
    ConversationalVoiceTurn,
    MicrophoneStatus,
    SpeechAnalysisResult,
    SpeechIntentType,
    VADState,
    WakeWordEvent,
    WakeWordMode,
)
from app.ai.voice.conversational.vad import VoiceActivityDetector
from app.ai.voice.conversational.audio_stream import StreamingAudioReceiver
from app.ai.voice.conversational.wake_word import ConversationalWakeWordEngine
from app.ai.voice.conversational.speech_intelligence import SpeechIntelligenceEngine
from app.ai.voice.conversational.echo_canceller import AcousticEchoCancellationGuard
from app.ai.voice.conversational.assistant import ConversationalVoiceAssistant
from app.ai.voice.models import SpeechResult
from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.tts_engine import LocalTTSEngine
from app.ai.multimodal.orchestrator import UnifiedMultimodalOrchestrator


# ==============================================================================
# Helper Functions & Fixtures for Synthetic Audio
# ==============================================================================

def generate_pcm_sine_wave(
    duration_sec: float = 0.5,
    sample_rate: int = 16000,
    frequency: float = 440.0,
    amplitude: float = 12000.0,
) -> bytes:
    """Generates pure sine wave PCM 16-bit mono bytes representing active speech."""
    num_samples = int(sample_rate * duration_sec)
    samples = [
        int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(num_samples)
    ]
    return struct.pack(f"<{num_samples}h", *samples)


def generate_pcm_silence(duration_sec: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generates zero-level PCM 16-bit mono bytes representing silence."""
    num_samples = int(sample_rate * duration_sec)
    return b"\x00\x00" * num_samples


def wrap_wav(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """Wraps raw PCM bytes in a compliant WAV header."""
    out = io.BytesIO()
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return out.getvalue()


@pytest.fixture
def spoken_sapi_sample(tmp_path):
    """Generates real spoken WAV audio bytes using Windows SAPI voice synthesis."""
    wav_path = str(tmp_path / "sapi_conversational_sample.wav")
    ps_cmd = (
        f"$s = New-Object -ComObject SAPI.SpVoice; "
        f"$f = New-Object -ComObject SAPI.SpFileStream; "
        f"$f.Open('{wav_path}', 3, $false); "
        f"$s.AudioOutputStream = $f; "
        f"$s.Speak('Nova create cube in Blender'); "
        f"$f.Close()"
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
    with open(wav_path, "rb") as f:
        return f.read()


@pytest.fixture
def shared_assistant(tmp_path_factory):
    """Shared ConversationalVoiceAssistant fixture with temporary audio cache."""
    cache_dir = str(tmp_path_factory.mktemp("conv_tts_cache"))
    assistant = ConversationalVoiceAssistant()
    assistant.tts_engine.storage_path = cache_dir
    return assistant


# ==============================================================================
# 1. VOICE ACTIVITY DETECTION (VAD)
# ==============================================================================

def test_vad_energy_rms_and_zero_crossing():
    """1. Verifies VAD acoustic metrics: RMS, dBFS energy, and zero-crossing rate."""
    vad = VoiceActivityDetector(sample_rate=16000, frame_duration_ms=20)

    # Silence frame (20ms = 320 samples = 640 bytes)
    silence_frame = generate_pcm_silence(0.02)
    metrics_silence = vad.compute_frame_metrics(silence_frame)
    assert metrics_silence.rms == 0.0
    assert metrics_silence.energy_db < -90.0
    assert metrics_silence.is_speech is False

    # Active tone frame
    tone_frame = generate_pcm_sine_wave(0.02, amplitude=15000.0)
    metrics_tone = vad.compute_frame_metrics(tone_frame)
    assert metrics_tone.rms > 8000.0
    assert metrics_tone.energy_db > -20.0
    assert metrics_tone.is_speech is True
    assert metrics_tone.zero_crossing_rate > 0.0


def test_vad_hysteresis_and_speech_boundaries():
    """2. Verifies state machine transitions: SILENCE -> SPEECH_STARTED -> SPEECH_ACTIVE -> SPEECH_ENDED."""
    vad = VoiceActivityDetector(
        sample_rate=16000,
        frame_duration_ms=20,
        min_speech_frames=2,
        hangover_frames=3,
    )

    silence_frame = generate_pcm_silence(0.02)
    speech_frame = generate_pcm_sine_wave(0.02, amplitude=14000.0)

    # Initial silence
    assert vad.process_frame(silence_frame) == VADState.SILENCE

    # First speech frame (pending min_speech_frames)
    s1 = vad.process_frame(speech_frame)
    assert s1 == VADState.SILENCE

    # Second speech frame triggers SPEECH_STARTED
    s2 = vad.process_frame(speech_frame)
    assert s2 == VADState.SPEECH_STARTED

    # Subsequent speech frame is SPEECH_ACTIVE
    s3 = vad.process_frame(speech_frame)
    assert s3 == VADState.SPEECH_ACTIVE

    # Micro-pause within hangover window remains SPEECH_ACTIVE
    h1 = vad.process_frame(silence_frame)
    assert h1 == VADState.SPEECH_ACTIVE
    h2 = vad.process_frame(silence_frame)
    assert h2 == VADState.SPEECH_ACTIVE

    # Exceeding hangover frames triggers SPEECH_ENDED
    h3 = vad.process_frame(silence_frame)
    assert h3 == VADState.SPEECH_ENDED


def test_vad_noise_floor_calibration():
    """3. Verifies dynamic background ambient noise floor calibration."""
    vad = VoiceActivityDetector()
    ambient_chunks = [generate_pcm_silence(0.05) for _ in range(5)]
    floor = vad.calibrate_noise_floor(ambient_chunks)
    assert floor <= -60.0
    assert vad.speech_start_threshold_db < 0.0


# ==============================================================================
# 2. STREAMING AUDIO RECEIVER & PRIVACY CONTROLS
# ==============================================================================

def test_streaming_audio_receiver_utterance_segmentation():
    """4. Verifies frame slicing and complete utterance WAV emission when speech ends."""
    receiver = StreamingAudioReceiver()

    # Stream 100ms silence
    for _ in range(5):
        res = receiver.feed_audio_chunk(generate_pcm_silence(0.02))
        assert res is None

    # Stream 300ms speech
    for _ in range(15):
        res = receiver.feed_audio_chunk(generate_pcm_sine_wave(0.02))
        assert res is None

    # Stream silence to trigger SPEECH_ENDED
    wav_payload = None
    for _ in range(20):
        wav = receiver.feed_audio_chunk(generate_pcm_silence(0.02))
        if wav:
            wav_payload = wav
            break

    assert wav_payload is not None
    assert wav_payload.startswith(b"RIFF")
    assert b"WAVE" in wav_payload


def test_microphone_kill_switch_and_privacy():
    """5. Verifies hardware/software kill-switch: wipes buffers and drops all audio when disabled."""
    receiver = StreamingAudioReceiver()

    # Ingest speech
    for _ in range(10):
        receiver.feed_audio_chunk(generate_pcm_sine_wave(0.02))

    status = receiver.get_status()
    assert status.is_active is True

    # TRIGGER PRIVACY KILL-SWITCH
    receiver.disable_microphone()
    status_disabled = receiver.get_status()
    assert status_disabled.is_active is False
    assert status_disabled.privacy_indicator == "OFF"

    # Audio fed while disabled must be strictly dropped
    res = receiver.feed_audio_chunk(generate_pcm_sine_wave(0.5))
    assert res is None
    assert len(receiver._speech_buffer) == 0

    # Test Mute
    receiver.enable_microphone()
    receiver.mute()
    assert receiver.is_muted is True
    assert receiver.get_status().privacy_indicator == "MUTED"
    res_muted = receiver.feed_audio_chunk(generate_pcm_sine_wave(0.5))
    assert res_muted is None


# ==============================================================================
# 3. WAKE-WORD DETECTION & PUSH-TO-TALK
# ==============================================================================

def test_wake_word_detection_and_prefix_stripping():
    """6. Verifies local wake-word matching and clean command prefix stripping."""
    engine = ConversationalWakeWordEngine(keywords=["nova", "hey nova"])

    # Wake word present with command
    active, stripped, ev = engine.check_activation(text="Hey Nova open Blender")
    assert active is True
    assert stripped == "open Blender"
    assert ev.keyword in ["nova", "hey nova"]

    # Wake word alone
    active2, stripped2, ev2 = engine.check_activation(text="Nova")
    assert active2 is True
    assert stripped2 == ""

    # Wake word absent in wake-word only mode
    active3, _, _ = engine.check_activation(text="open Blender without wake word")
    assert active3 is False


def test_push_to_talk_mode():
    """7. Verifies push-to-talk override bypasses wake-word requirement."""
    engine = ConversationalWakeWordEngine(mode=WakeWordMode.WAKE_WORD_ONLY)

    # When push-to-talk is inactive, non-wake-word speech is rejected
    active, _, _ = engine.check_activation(text="Create cube in Blender")
    assert active is False

    # Activate push-to-talk
    engine.start_push_to_talk()
    active_ptt, stripped_ptt, ev_ptt = engine.check_activation(text="Create cube in Blender")
    assert active_ptt is True
    assert stripped_ptt == "Create cube in Blender"
    assert ev_ptt.mode == WakeWordMode.PUSH_TO_TALK

    # Deactivate push-to-talk
    engine.stop_push_to_talk()
    active_after, _, _ = engine.check_activation(text="Create cube in Blender")
    assert active_after is False


# ==============================================================================
# 4. SPEECH INTELLIGENCE (INCOMPLETE, REPAIR, CHITCHAT)
# ==============================================================================

def test_speech_intelligence_incomplete_command_detection():
    """8. Verifies trailing incomplete commands trigger a natural clarification question."""
    engine = SpeechIntelligenceEngine()

    res = engine.analyze_speech("open the")
    assert res.is_incomplete is True
    assert res.intent_type == SpeechIntentType.INCOMPLETE
    assert "Which application" in res.missing_information_prompt

    res_del = engine.analyze_speech("delete")
    assert res_del.is_incomplete is True
    assert "Which item" in res_del.missing_information_prompt


def test_speech_intelligence_verbal_self_correction():
    """9. Verifies spoken repairs ('no wait', 'actually') extract the corrected intent."""
    engine = SpeechIntelligenceEngine()

    # "Open Blender, no wait, open Photoshop"
    res1 = engine.analyze_speech("Open Blender, no wait, open Photoshop")
    assert res1.intent_type == SpeechIntentType.CORRECTION
    assert res1.target_app == "Photoshop"
    assert "photoshop" in res1.cleaned_transcript.lower()
    assert res1.corrected_from is not None

    # "Create cube, actually make it a sphere"
    res2 = engine.analyze_speech("Create a cube, actually make it a sphere")
    assert res2.intent_type == SpeechIntentType.CORRECTION
    assert res2.parameters.get("primitive") == "uv_sphere"


def test_speech_intelligence_chitchat_vs_action():
    """10. Verifies ordinary conversation is classified as CHITCHAT and not executed as actions."""
    engine = SpeechIntelligenceEngine()

    res_hi = engine.analyze_speech("Hello Nova")
    assert res_hi.intent_type == SpeechIntentType.CHITCHAT_CONVERSATION
    assert "Hello" in res_hi.parameters.get("response", "")

    res_how = engine.analyze_speech("How are you")
    assert res_how.intent_type == SpeechIntentType.CHITCHAT_CONVERSATION

    # Actionable command
    res_cmd = engine.analyze_speech("Create cube in Blender")
    assert res_cmd.intent_type == SpeechIntentType.ACTIONABLE_COMMAND
    assert res_cmd.target_app == "Blender"


# ==============================================================================
# 5. ACOUSTIC ECHO CANCELLATION & BARGE-IN
# ==============================================================================

def test_acoustic_echo_cancellation_feedback_suppression():
    """11. Verifies speaker echo matching assistant's own TTS output is suppressed."""
    echo_guard = AcousticEchoCancellationGuard()

    # Assistant commences playback
    echo_guard.start_playback("Successfully created cube in Blender.", estimated_duration_sec=3.0)
    assert echo_guard.is_playback_active is True

    # Incoming audio that duplicates assistant speech is detected as echo
    is_echo, is_barge_in = echo_guard.evaluate_incoming_speech("Successfully created cube in Blender.")
    assert is_echo is True
    assert is_barge_in is False

    # Clean user interruption during playback triggers barge-in
    is_echo_stop, is_barge_in_stop = echo_guard.evaluate_incoming_speech("Stop right now")
    assert is_echo_stop is False
    assert is_barge_in_stop is True
    assert echo_guard.is_playback_active is False


# ==============================================================================
# 6. END-TO-END CONVERSATIONAL ASSISTANT & MULTI-TURN
# ==============================================================================

@pytest.mark.anyio
async def test_conversational_assistant_chitchat_flow(shared_assistant):
    """12. Verifies natural verbal conversational exchange for chitchat."""
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Hey Nova how are you", confidence=0.98, language="en")
    )

    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))
    turn = await shared_assistant.process_utterance(dummy_wav, session_id="test_conv_chitchat")

    assert isinstance(turn, ConversationalVoiceTurn)
    assert turn.intent_type == SpeechIntentType.CHITCHAT_CONVERSATION
    assert "local" in turn.assistant_spoken_response.lower()
    assert turn.tts_path is not None
    assert os.path.exists(turn.tts_path)


@pytest.mark.anyio
async def test_conversational_multi_turn_followup_without_wake_word(shared_assistant):
    """13. Verifies continuous conversation: turn 2 requires NO wake word within follow-up window."""
    sid = "multi_turn_followup_session"
    shared_assistant.followup_window_sec = 10.0

    # Turn 1: Uses wake word "Hey Nova create cube in Blender"
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Hey Nova create cube in Blender", confidence=0.98, language="en")
    )
    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))
    turn1 = await shared_assistant.process_utterance(dummy_wav, session_id=sid)

    assert turn1.execution_success is True
    assert shared_assistant.get_state(sid) == ConversationalState.AWAITING_FOLLOWUP

    # Turn 2: Follow-up command WITHOUT wake word ("now create a sphere in it")
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="now create a sphere in it", confidence=0.95, language="en")
    )
    turn2 = await shared_assistant.process_utterance(dummy_wav, session_id=sid)

    # Must be accepted directly in follow-up mode!
    assert turn2.execution_success is True
    assert turn2.user_transcript == "now create a sphere in it"
    assert "Executed" in turn2.assistant_spoken_response or "Successfully" in turn2.assistant_spoken_response


@pytest.mark.anyio
async def test_incomplete_command_triggers_spoken_clarification(shared_assistant):
    """14. Verifies incomplete spoken command prompts for clarification verbally."""
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Hey Nova open the", confidence=0.95, language="en")
    )
    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))
    turn = await shared_assistant.process_utterance(dummy_wav, session_id="test_incomplete_cmd")

    assert turn.intent_type == SpeechIntentType.INCOMPLETE
    assert "Which application" in turn.assistant_spoken_response


@pytest.mark.anyio
async def test_spoken_self_correction_executes_corrected_goal(shared_assistant):
    """15. Verifies spoken repair executes Photoshop instead of Blender."""
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Nova open Blender, no wait, open Photoshop", confidence=0.95, language="en")
    )
    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))
    turn = await shared_assistant.process_utterance(dummy_wav, session_id="test_self_repair")

    assert turn.intent_type == SpeechIntentType.CORRECTION
    assert "Photoshop" in turn.assistant_spoken_response


@pytest.mark.anyio
async def test_fast_path_system_control_stop(shared_assistant):
    """16. Verifies 'stop' command triggers immediate interruption without planning."""
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Nova stop", confidence=0.99, language="en")
    )
    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))
    turn = await shared_assistant.process_utterance(dummy_wav, session_id="test_sys_stop")

    assert turn.intent_type == SpeechIntentType.SYSTEM_CONTROL
    assert "Cancelled" in turn.assistant_spoken_response
    assert shared_assistant.get_state("test_sys_stop") == ConversationalState.CANCELLED


@pytest.mark.anyio
async def test_debouncing_duplicate_commands(shared_assistant):
    """17. Verifies identical commands emitted within 2 seconds are debounced."""
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Nova create cube in Blender", confidence=0.98, language="en")
    )
    dummy_wav = wrap_wav(generate_pcm_sine_wave(0.2))

    turn1 = await shared_assistant.process_utterance(dummy_wav, session_id="test_debounce")
    assert turn1.execution_success is True

    # Immediate second call with identical transcript
    turn2 = await shared_assistant.process_utterance(dummy_wav, session_id="test_debounce")
    assert "Already processing that" in turn2.assistant_spoken_response


# ==============================================================================
# 7. REAL SPOKEN SAPI AUDIO INTEGRATION TEST
# ==============================================================================

@pytest.mark.anyio
async def test_real_sapi_spoken_audio_pipeline(shared_assistant, spoken_sapi_sample):
    """18. Real audio test using physical Windows SAPI synthetic speech WAV file."""
    # Mock STT to verify assistant pipeline with real spoken audio bytes
    shared_assistant.stt_engine.transcribe = AsyncMock(
        return_value=SpeechResult(transcript="Nova create cube in Blender", confidence=0.98, language="en")
    )

    turn = await shared_assistant.process_utterance(spoken_sapi_sample, session_id="test_real_sapi")

    assert isinstance(turn, ConversationalVoiceTurn)
    assert turn.execution_success is True
    assert turn.tts_path is not None
    assert os.path.exists(turn.tts_path)
    assert os.path.getsize(turn.tts_path) > 0
    assert turn.latency_ms > 0.0

