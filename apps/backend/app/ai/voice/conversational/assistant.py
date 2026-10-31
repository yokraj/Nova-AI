"""Real-Time Conversational Voice Assistant for Nova-AI (Phase 10M-B).

Connects streaming microphone audio, VAD, local wake-word, speech intelligence,
multi-turn context, echo cancellation, and canonical execution into a unified conversational agent.
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
import hashlib
import re
import time
import uuid
import structlog

from app.ai.voice.conversational.models import (
    ConversationalSession,
    ConversationalState,
    ConversationalVoiceTurn,
    MicrophoneStatus,
    SpeechAnalysisResult,
    SpeechIntentType,
    WakeWordMode,
)
from app.ai.voice.conversational.audio_stream import StreamingAudioReceiver
from app.ai.voice.conversational.vad import VoiceActivityDetector
from app.ai.voice.conversational.wake_word import ConversationalWakeWordEngine
from app.ai.voice.conversational.speech_intelligence import SpeechIntelligenceEngine
from app.ai.voice.conversational.echo_canceller import AcousticEchoCancellationGuard
from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.tts_engine import LocalTTSEngine
from app.ai.voice.security_filter import VoiceSecurityFilter, VoiceSecurityError
from app.ai.multimodal.orchestrator import UnifiedMultimodalOrchestrator
from app.ai.multimodal.context_manager import MultimodalContextManager
from app.ai.multimodal.models import InputModality, InteractionState

logger = structlog.get_logger("conversational_voice_assistant")


class ConversationalVoiceAssistant:
    """Enterprise real-time conversational voice assistant with full local execution."""

    def __init__(
        self,
        stt_engine: Optional[LocalSTTEngine] = None,
        tts_engine: Optional[LocalTTSEngine] = None,
        multimodal_orchestrator: Optional[UnifiedMultimodalOrchestrator] = None,
        context_manager: Optional[MultimodalContextManager] = None,
        wake_word_engine: Optional[ConversationalWakeWordEngine] = None,
        speech_intelligence: Optional[SpeechIntelligenceEngine] = None,
        audio_receiver: Optional[StreamingAudioReceiver] = None,
        echo_canceller: Optional[AcousticEchoCancellationGuard] = None,
        followup_window_sec: float = 6.0,
        stt_timeout_sec: float = 30.0,
        tts_timeout_sec: float = 10.0,
    ) -> None:
        self.stt_engine = stt_engine or LocalSTTEngine()
        self.tts_engine = tts_engine or LocalTTSEngine()
        self.multimodal_orchestrator = multimodal_orchestrator or UnifiedMultimodalOrchestrator()
        self.context_manager = context_manager or getattr(self.multimodal_orchestrator, "context_manager", MultimodalContextManager())
        self.wake_word_engine = wake_word_engine or ConversationalWakeWordEngine()
        self.speech_intelligence = speech_intelligence or SpeechIntelligenceEngine()
        self.audio_receiver = audio_receiver or StreamingAudioReceiver()
        self.echo_canceller = echo_canceller or AcousticEchoCancellationGuard()

        self.followup_window_sec = followup_window_sec
        self.stt_timeout_sec = stt_timeout_sec
        self.tts_timeout_sec = tts_timeout_sec

        self._sessions: Dict[str, ConversationalSession] = {}
        self._recent_command_hashes: Dict[str, float] = {}  # For debouncing / idempotency

    # --------------------------------------------------------------------------
    # Session Management & Lifecycle
    # --------------------------------------------------------------------------

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationalSession:
        """Retrieves or creates a tracking conversational voice session."""
        sid = session_id or f"voice_sess_{uuid.uuid4().hex[:8]}"
        if sid not in self._sessions:
            self._sessions[sid] = ConversationalSession(
                session_id=sid,
                state=ConversationalState.IDLE,
                wake_word_mode=self.wake_word_engine.mode,
                followup_window_sec=self.followup_window_sec,
            )
        return self._sessions[sid]

    def get_state(self, session_id: str) -> ConversationalState:
        """Returns the current state for a voice session."""
        session = self.get_or_create_session(session_id)
        return session.state

    def set_state(self, session_id: str, state: ConversationalState) -> None:
        """Updates the state for a session and logs telemetry."""
        session = self.get_or_create_session(session_id)
        session.state = state
        session.mic_status.state = state
        logger.debug("Conversational session state updated", session_id=session_id, state=state.value)

    # --------------------------------------------------------------------------
    # Hardware & Privacy Kill-Switch Controls
    # --------------------------------------------------------------------------

    def enable_microphone(self, session_id: Optional[str] = None) -> MicrophoneStatus:
        """Enables microphone input stream."""
        self.audio_receiver.enable_microphone()
        status = self.audio_receiver.get_status()
        if session_id:
            sess = self.get_or_create_session(session_id)
            sess.mic_status = status
            if sess.state == ConversationalState.MUTED:
                sess.state = ConversationalState.IDLE
        return status

    def disable_microphone(self, session_id: Optional[str] = None) -> MicrophoneStatus:
        """Hardware/Software Kill-Switch: immediately wipes audio buffers and drops all input."""
        self.audio_receiver.disable_microphone()
        status = self.audio_receiver.get_status()
        if session_id:
            sess = self.get_or_create_session(session_id)
            sess.mic_status = status
            sess.state = ConversationalState.MUTED
        return status

    def mute(self, session_id: Optional[str] = None) -> MicrophoneStatus:
        """Mutes audio input."""
        self.audio_receiver.mute()
        status = self.audio_receiver.get_status()
        if session_id:
            sess = self.get_or_create_session(session_id)
            sess.mic_status = status
            sess.state = ConversationalState.MUTED
        return status

    def unmute(self, session_id: Optional[str] = None) -> MicrophoneStatus:
        """Unmutes audio input."""
        self.audio_receiver.unmute()
        status = self.audio_receiver.get_status()
        if session_id:
            sess = self.get_or_create_session(session_id)
            sess.mic_status = status
            if sess.state == ConversationalState.MUTED:
                sess.state = ConversationalState.IDLE
        return status

    def start_push_to_talk(self, session_id: Optional[str] = None) -> None:
        """Activates push-to-talk mode for immediate speech input."""
        self.wake_word_engine.start_push_to_talk()
        if session_id:
            self.set_state(session_id, ConversationalState.LISTENING)

    def stop_push_to_talk(self, session_id: Optional[str] = None) -> None:
        """Deactivates push-to-talk mode."""
        self.wake_word_engine.stop_push_to_talk()
        if session_id and self.get_state(session_id) == ConversationalState.LISTENING:
            self.set_state(session_id, ConversationalState.IDLE)

    def interrupt(self, session_id: str) -> bool:
        """Barge-In: user interruption during speaking or execution."""
        logger.info("Conversational barge-in interrupt triggered", session_id=session_id)
        self.echo_canceller.stop_playback()
        self.multimodal_orchestrator.voice_interface.interrupt(session_id)
        self.set_state(session_id, ConversationalState.CANCELLED)
        return True

    # --------------------------------------------------------------------------
    # Streaming Audio Ingestion & Interaction Processing
    # --------------------------------------------------------------------------

    async def process_audio_chunk(
        self,
        chunk: bytes,
        session_id: Optional[str] = None,
    ) -> Optional[ConversationalVoiceTurn]:
        """Processes streaming microphone chunk.

        If a full utterance is detected by VAD (SPEECH_ENDED), transcribes, analyzes,
        and dispatches to the canonical execution pipeline.

        Returns:
            ConversationalVoiceTurn if an utterance was completed and processed, else None.
        """
        session = self.get_or_create_session(session_id)

        # 1. Echo Cancellation & Interruption Check
        if self.echo_canceller.is_playback_active:
            frame_metrics = self.audio_receiver.vad.compute_frame_metrics(chunk)
            if frame_metrics.is_speech and frame_metrics.energy_db > -35.0:
                logger.info("Acoustic energy exceeded threshold during playback; triggering barge-in", session_id=session.session_id)
                self.interrupt(session.session_id)

        # 2. Feed chunk into audio receiver
        completed_utterance_wav = self.audio_receiver.feed_audio_chunk(chunk)
        if not completed_utterance_wav:
            return None

        # 3. Process completed utterance
        return await self.process_utterance(completed_utterance_wav, session_id=session.session_id)

    async def process_utterance(
        self,
        audio_wav_bytes: bytes,
        session_id: Optional[str] = None,
    ) -> ConversationalVoiceTurn:
        """Processes a complete speech WAV audio payload through the full conversational pipeline."""
        start_time = time.perf_counter()
        session = self.get_or_create_session(session_id)
        sid = session.session_id

        self.set_state(sid, ConversationalState.PROCESSING)

        # 1. Speech-To-Text Transcription
        try:
            speech_result = await asyncio.wait_for(
                self.stt_engine.transcribe(audio_wav_bytes),
                timeout=self.stt_timeout_sec,
            )
            raw_transcript = speech_result.transcript.strip()
            detected_lang = getattr(speech_result, "language", "en")
        except asyncio.TimeoutError:
            logger.warning("STT transcription timed out", session_id=sid)
            return await self._create_error_turn(sid, "STT timed out", "I took too long to hear you. Could you repeat that?", start_time)
        except Exception as e:
            logger.error("STT transcription failed", error=str(e), session_id=sid)
            return await self._create_error_turn(sid, str(e), "I had trouble processing that audio. Please try again.", start_time)

        # 2. Echo Cancellation Check
        is_echo, is_barge_in = self.echo_canceller.evaluate_incoming_speech(raw_transcript)
        if is_echo:
            logger.info("Discarded utterance matching assistant's own TTS output", transcript=raw_transcript)
            self.set_state(sid, ConversationalState.IDLE)
            return ConversationalVoiceTurn(
                turn_id=f"turn_{uuid.uuid4().hex[:8]}",
                session_id=sid,
                user_transcript=raw_transcript,
                assistant_spoken_response="",
                intent_type=SpeechIntentType.CHITCHAT_CONVERSATION,
                execution_success=True,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        if is_barge_in:
            self.interrupt(sid)

        # 3. Wake-Word Activation & Prefix Stripping
        is_followup = session.is_in_followup_window()
        is_activated, stripped_text, wake_event = self.wake_word_engine.check_activation(
            text=raw_transcript,
            audio_chunk=audio_wav_bytes,
            is_in_followup_window=is_followup,
        )

        if not is_activated:
            logger.debug("Wake word not detected; ignoring audio utterance", transcript=raw_transcript)
            self.set_state(sid, ConversationalState.IDLE)
            return ConversationalVoiceTurn(
                turn_id=f"turn_{uuid.uuid4().hex[:8]}",
                session_id=sid,
                user_transcript=raw_transcript,
                assistant_spoken_response="",
                intent_type=SpeechIntentType.CHITCHAT_CONVERSATION,
                execution_success=False,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )

        effective_transcript = stripped_text if stripped_text else raw_transcript

        # 4. Debounce / Idempotency Check
        transcript_hash = hashlib.sha256(effective_transcript.lower().encode("utf-8")).hexdigest()
        now = time.time()
        last_seen = self._recent_command_hashes.get(transcript_hash, 0.0)
        if (now - last_seen) < 10.0:
            logger.info("Suppressed duplicate voice command within debounce window", transcript=effective_transcript)
            self.set_state(sid, ConversationalState.AWAITING_FOLLOWUP)
            return ConversationalVoiceTurn(
                turn_id=f"turn_{uuid.uuid4().hex[:8]}",
                session_id=sid,
                user_transcript=effective_transcript,
                assistant_spoken_response="Already processing that.",
                intent_type=SpeechIntentType.ACTIONABLE_COMMAND,
                execution_success=True,
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
            )
        self._recent_command_hashes[transcript_hash] = now

        # 5. Speech Intelligence: Incomplete, Repair, Intent Categorization
        analysis: SpeechAnalysisResult = self.speech_intelligence.analyze_speech(
            transcript=effective_transcript,
            language=detected_lang,
            has_active_task=bool(session.active_task_id),
        )

        # 6. Dispatch based on Classified Intent Type

        # Case A: System Control (Stop, Cancel, Mute)
        if analysis.intent_type == SpeechIntentType.SYSTEM_CONTROL:
            control_action = analysis.parameters.get("action", "STOP")
            if control_action in ["STOP", "CANCEL"]:
                self.interrupt(sid)
                spoken = "Cancelled current action."
                target_state = ConversationalState.CANCELLED
            elif control_action == "MUTE":
                self.mute(sid)
                spoken = "Microphone muted. Say unmute or press talk to resume."
                target_state = ConversationalState.MUTED
            else:
                spoken = f"Executing {control_action.lower()}."
                target_state = ConversationalState.AWAITING_FOLLOWUP

            turn = await self._formulate_turn(sid, effective_transcript, spoken, analysis.intent_type, start_time)
            self.set_state(sid, target_state)
            return turn

        # Case B: Incomplete Command (Prompts user for missing information)
        if analysis.is_incomplete:
            spoken_prompt = analysis.missing_information_prompt or "Could you clarify what you would like me to do?"
            self.set_state(sid, ConversationalState.AWAITING_FOLLOWUP)
            return await self._formulate_turn(sid, effective_transcript, spoken_prompt, SpeechIntentType.INCOMPLETE, start_time)

        # Case C: Chitchat / General Inquiry (Direct Conversational Response)
        if analysis.intent_type == SpeechIntentType.CHITCHAT_CONVERSATION:
            chitchat_reply = analysis.parameters.get("response", "I'm ready for your command.")
            self.set_state(sid, ConversationalState.AWAITING_FOLLOWUP)
            return await self._formulate_turn(sid, effective_transcript, chitchat_reply, SpeechIntentType.CHITCHAT_CONVERSATION, start_time)

        # Case D: Actionable Command or Corrected Goal -> Canonical Execution Pipeline
        self.set_state(sid, ConversationalState.PLANNING)

        # Pass through Security Filter
        try:
            VoiceSecurityFilter.inspect_transcript(analysis.cleaned_transcript)
        except VoiceSecurityError as sec_err:
            spoken_err = f"Security block: {str(sec_err)}"
            self.set_state(sid, ConversationalState.AWAITING_FOLLOWUP)
            return await self._formulate_turn(sid, effective_transcript, spoken_err, SpeechIntentType.ACTIONABLE_COMMAND, start_time, success=False)
        except Exception:
            pass  # Approval required or standard inspection

        # Route to UnifiedMultimodalOrchestrator
        self.set_state(sid, ConversationalState.EXECUTING)
        task_id: Optional[str] = None
        exec_success = True

        try:
            exec_res = await self.multimodal_orchestrator.process_text(
                text=analysis.cleaned_transcript,
                session_id=sid,
                active_app_override=analysis.target_app,
            )
            task_id = exec_res.task_id
            exec_success = exec_res.success
            raw_response = exec_res.spoken_response or f"Finished executing {analysis.target_goal}."
        except Exception as e:
            logger.error("Canonical execution failed for spoken command", error=str(e), transcript=analysis.cleaned_transcript)
            raw_response = f"Execution failed for {analysis.cleaned_transcript}. Please try again."
            exec_success = False

        # Make response natural and conversational (strip code/markdown/tables)
        spoken_response = self._make_natural_spoken_text(raw_response)
        session.active_task_id = task_id
        session.active_app = analysis.target_app or session.active_app

        self.set_state(sid, ConversationalState.AWAITING_FOLLOWUP)
        return await self._formulate_turn(
            sid,
            effective_transcript,
            spoken_response,
            analysis.intent_type,
            start_time,
            task_id=task_id,
            success=exec_success,
        )

    # --------------------------------------------------------------------------
    # TTS Formulation & Helper Methods
    # --------------------------------------------------------------------------

    async def _formulate_turn(
        self,
        session_id: str,
        user_transcript: str,
        spoken_text: str,
        intent_type: SpeechIntentType,
        start_time: float,
        task_id: Optional[str] = None,
        success: bool = True,
    ) -> ConversationalVoiceTurn:
        """Synthesizes voice audio response via LocalTTSEngine and logs turn."""
        session = self.get_or_create_session(session_id)
        tts_path: Optional[str] = None

        if spoken_text:
            self.set_state(session_id, ConversationalState.SPEAKING)
            # Notify echo canceller of upcoming playback
            est_duration = max(1.0, len(spoken_text) * 0.06)
            self.echo_canceller.start_playback(spoken_text, estimated_duration_sec=est_duration)

            try:
                tts_path = await asyncio.wait_for(
                    self.tts_engine.synthesize(spoken_text),
                    timeout=self.tts_timeout_sec,
                )
            except Exception as e:
                logger.warning("TTS generation encountered non-fatal error", error=str(e))
                tts_path = None
            finally:
                self.echo_canceller.stop_playback()
                if self.get_state(session_id) not in [ConversationalState.CANCELLED, ConversationalState.MUTED]:
                    self.set_state(session_id, ConversationalState.AWAITING_FOLLOWUP)

        turn = ConversationalVoiceTurn(
            turn_id=f"turn_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            user_transcript=user_transcript,
            assistant_spoken_response=spoken_text,
            intent_type=intent_type,
            task_id=task_id,
            execution_success=success,
            tts_path=tts_path,
            latency_ms=(time.perf_counter() - start_time) * 1000.0,
        )
        session.add_turn(turn)
        return turn

    async def _create_error_turn(
        self,
        session_id: str,
        error_msg: str,
        spoken_response: str,
        start_time: float,
    ) -> ConversationalVoiceTurn:
        """Generates an error turn with spoken fallback."""
        self.set_state(session_id, ConversationalState.AWAITING_FOLLOWUP)
        return await self._formulate_turn(
            session_id=session_id,
            user_transcript="",
            spoken_text=spoken_response,
            intent_type=SpeechIntentType.CHITCHAT_CONVERSATION,
            start_time=start_time,
            success=False,
        )

    @staticmethod
    def _make_natural_spoken_text(text: str) -> str:
        """Strips markdown asterisks, backticks, URLs, and code blocks for speech synthesis."""
        if not text:
            return ""
        # Remove code blocks
        clean = re.sub(r"```[\s\S]*?```", "", text)
        # Remove markdown inline formatting
        clean = re.sub(r"[`*_{}\[\]()]", "", clean)
        # Remove URLs
        clean = re.sub(r"https?://\S+", "", clean)
        # Collapse multiple whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        # Ensure it ends with punctuation
        if clean and not clean.endswith((".", "!", "?")):
            clean += "."
        return clean

