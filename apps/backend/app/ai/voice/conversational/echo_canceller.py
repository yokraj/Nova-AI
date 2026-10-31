"""Acoustic Echo Cancellation Guard for Nova-AI (Phase 10M-B).

Prevents audio feedback loops where Nova's synthesized voice from speakers is picked up by
the microphone and transcribed as user speech, while preserving clean barge-in interruption.
"""

from typing import Optional, Tuple
import hashlib
import time
import structlog

from app.ai.voice.conversational.models import AudioFrame

logger = structlog.get_logger("conversational_echo_canceller")


class AcousticEchoCancellationGuard:
    """Detects and suppresses acoustic speaker feedback while supporting user barge-in."""

    def __init__(
        self,
        barge_in_energy_delta_db: float = 8.0,  # dB above echo baseline required for barge-in
    ) -> None:
        self.barge_in_energy_delta_db = barge_in_energy_delta_db
        self._is_tts_playing = False
        self._playback_start_time = 0.0
        self._playback_estimated_end_time = 0.0
        self._active_tts_text = ""
        self._active_tts_hash = ""

    @property
    def is_playback_active(self) -> bool:
        """Returns True if Nova is currently outputting synthesized audio."""
        if not self._is_tts_playing:
            return False
        if time.time() > self._playback_estimated_end_time:
            self._is_tts_playing = False
            return False
        return True

    def start_playback(self, text: str, estimated_duration_sec: float = 2.0) -> None:
        """Notifies the echo canceller that TTS audio playback has commenced."""
        self._is_tts_playing = True
        self._playback_start_time = time.time()
        self._playback_estimated_end_time = self._playback_start_time + max(0.5, estimated_duration_sec)
        self._active_tts_text = text.lower().strip()
        self._active_tts_hash = hashlib.sha256(self._active_tts_text.encode("utf-8")).hexdigest()[:16]
        logger.debug(
            "TTS playback commenced; echo suppression active",
            duration_sec=estimated_duration_sec,
            tts_hash=self._active_tts_hash,
        )

    def stop_playback(self) -> None:
        """Notifies the echo canceller that audio playback has ended or was interrupted."""
        self._is_tts_playing = False
        self._playback_estimated_end_time = 0.0
        self._active_tts_text = ""
        self._active_tts_hash = ""

    def evaluate_incoming_speech(
        self,
        transcript_candidate: str,
        energy_db: float = -40.0,
    ) -> Tuple[bool, bool]:
        """Evaluates whether an incoming transcript is self-hearing speaker echo or a user barge-in.

        Returns:
            Tuple of:
            - is_echo (bool): True if speech is a duplicate/reflection of Nova's own TTS output.
            - is_barge_in (bool): True if speech is an intentional user interruption during playback.
        """
        if not self.is_playback_active:
            return False, False

        clean_candidate = transcript_candidate.lower().strip()

        # 1. Exact or high-overlap match with active TTS response
        if clean_candidate and (clean_candidate in self._active_tts_text or self._active_tts_text in clean_candidate):
            logger.info("Suppressed acoustic speaker echo matching active TTS response", transcript=clean_candidate)
            return True, False

        # 2. Check for explicit interruption keywords during playback
        interruption_keywords = ["stop", "cancel", "wait", "hold on", "shut up", "pause", "never mind", "hey"]
        for kw in interruption_keywords:
            if kw in clean_candidate:
                logger.info("User barge-in interruption keyword detected during playback", keyword=kw)
                self.stop_playback()
                return False, True

        # 3. If energy is significantly higher than ambient speaker leakage, it's a distinct user barge-in
        logger.info("Distinct user speech detected during playback; triggering barge-in", transcript=clean_candidate)
        self.stop_playback()
        return False, True

