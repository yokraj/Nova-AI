"""Voice Experience Interface for Nova-AI Multimodal Engine.

Provides offline Whisper STT transcription, local TTS audio generation, state machine tracking,
and real-time interrupt and cancellation handling.
"""

from typing import Dict, Optional
import os
import structlog

from app.ai.multimodal.models import InteractionState
from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.tts_engine import LocalTTSEngine
from app.ai.voice.models import SpeechResult
from app.ai.voice.exceptions import SpeechRecognitionError, TextToSpeechError

logger = structlog.get_logger("multimodal_voice_interface")


class MultimodalVoiceInterface:
    """Manages voice input/output lifecycle, state changes, and barge-in interruptions."""

    def __init__(
        self,
        stt_engine: Optional[LocalSTTEngine] = None,
        tts_engine: Optional[LocalTTSEngine] = None,
    ) -> None:
        self.stt_engine = stt_engine or LocalSTTEngine()
        self.tts_engine = tts_engine or LocalTTSEngine()
        self._states: Dict[str, InteractionState] = {}
        self._interrupted: Dict[str, bool] = {}

    def is_offline_capable(self) -> bool:
        """Confirms that voice components operate purely locally without cloud dependencies."""
        return getattr(self.stt_engine, "is_offline", True) and getattr(self.tts_engine, "is_offline", True)

    def get_state(self, session_id: str) -> InteractionState:
        """Returns the current interaction state for a session."""
        return self._states.get(session_id, InteractionState.IDLE)

    def set_state(self, session_id: str, state: InteractionState) -> None:
        """Transitions interaction state for a session."""
        self._states[session_id] = state
        logger.debug("Voice interface state updated", session_id=session_id, state=state.value)

    def start_listening(self, session_id: str) -> None:
        """Transitions state to LISTENING."""
        self._interrupted[session_id] = False
        self.set_state(session_id, InteractionState.LISTENING)

    async def transcribe_audio(self, audio_bytes: bytes, session_id: str) -> SpeechResult:
        """Transcribes incoming audio bytes using local Whisper STT."""
        self.set_state(session_id, InteractionState.PROCESSING)
        if self.is_interrupted(session_id):
            self.set_state(session_id, InteractionState.CANCELLED)
            raise SpeechRecognitionError("Transcription aborted due to user interruption.")

        try:
            res = await self.stt_engine.transcribe(audio_bytes)
            return res
        except Exception as e:
            self.set_state(session_id, InteractionState.FAILED)
            raise

    async def speak(self, text: str, session_id: str) -> str:
        """Synthesizes text into spoken audio WAV file path using local TTS.

        Returns:
            Absolute file path to synthesized WAV audio file.
        """
        if self.is_interrupted(session_id):
            logger.info("Speech synthesis suppressed due to active interruption", session_id=session_id)
            self.set_state(session_id, InteractionState.CANCELLED)
            return ""

        self.set_state(session_id, InteractionState.SPEAKING)
        try:
            audio_path = await self.tts_engine.synthesize(text)
            self.set_state(session_id, InteractionState.COMPLETED)
            return audio_path
        except Exception as e:
            self.set_state(session_id, InteractionState.FAILED)
            logger.error("TTS audio synthesis failed", error=str(e), text=text)
            raise

    def interrupt(self, session_id: str) -> bool:
        """Triggers immediate barge-in interrupt signal for session."""
        logger.info("User barge-in interruption triggered", session_id=session_id)
        self._interrupted[session_id] = True
        self.set_state(session_id, InteractionState.CANCELLED)
        return True

    def cancel(self, session_id: str) -> bool:
        """Explicitly cancels active task and resets state."""
        return self.interrupt(session_id)

    def is_interrupted(self, session_id: str) -> bool:
        """Checks if session has an active cancellation / interruption signal."""
        return self._interrupted.get(session_id, False)

    def reset(self, session_id: str) -> None:
        """Resets session interruption and returns state to IDLE."""
        self._interrupted[session_id] = False
        self.set_state(session_id, InteractionState.IDLE)

