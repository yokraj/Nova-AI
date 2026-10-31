"""Local Wake-Word Engine and Push-to-Talk Manager for Nova-AI (Phase 10M-B).

Provides offline keyword detection ("Nova", "Hey Nova"), configurable trigger modes,
push-to-talk fallbacks, and command prefix stripping.
"""

from typing import List, Optional, Tuple
import re
import structlog

from app.ai.voice.conversational.models import WakeWordEvent, WakeWordMode

logger = structlog.get_logger("conversational_wake_word")


class ConversationalWakeWordEngine:
    """Detects configurable wake words locally and handles push-to-talk activation."""

    DEFAULT_KEYWORDS = ["nova", "hey nova"]

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        mode: WakeWordMode = WakeWordMode.WAKE_WORD_ONLY,
        confidence_threshold: float = 0.85,
    ) -> None:
        self.keywords = [k.strip().lower() for k in (keywords or self.DEFAULT_KEYWORDS)]
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self._push_to_talk_active = False

    def set_mode(self, mode: WakeWordMode) -> None:
        """Configures the active listening mode."""
        self.mode = mode
        logger.info("Wake word mode updated", mode=mode.value)

    def start_push_to_talk(self) -> None:
        """Enables push-to-talk override."""
        self._push_to_talk_active = True
        logger.info("Push-to-talk activated")

    def stop_push_to_talk(self) -> None:
        """Disables push-to-talk override."""
        self._push_to_talk_active = False
        logger.info("Push-to-talk deactivated")

    def check_activation(
        self,
        text: Optional[str] = None,
        audio_chunk: Optional[bytes] = None,
        is_in_followup_window: bool = False,
    ) -> Tuple[bool, Optional[str], Optional[WakeWordEvent]]:
        """Evaluates whether speech should trigger assistant processing.

        Args:
            text: Transcribed speech text (if available).
            audio_chunk: Raw audio bytes for phonetic/ASCII scanning.
            is_in_followup_window: True if assistant is currently in an active multi-turn session.

        Returns:
            Tuple of:
            - is_activated: bool
            - stripped_command: Optional[str] (text with wake word prefix removed)
            - event: Optional[WakeWordEvent]
        """
        # 1. Push-to-Talk Override
        if self.mode == WakeWordMode.PUSH_TO_TALK or self._push_to_talk_active:
            event = WakeWordEvent(
                keyword="push_to_talk",
                detected=True,
                confidence=1.0,
                mode=WakeWordMode.PUSH_TO_TALK,
            )
            return True, text or "", event

        # 2. Continuous Multi-Turn Conversation Mode
        if self.mode == WakeWordMode.CONTINUOUS_CONVERSATION or is_in_followup_window:
            event = WakeWordEvent(
                keyword="followup_context",
                detected=True,
                confidence=1.0,
                mode=WakeWordMode.CONTINUOUS_CONVERSATION,
            )
            clean_text = self._strip_wake_word_prefix(text) if text else (text or "")
            return True, clean_text, event

        # 3. Wake-Word Only Mode: Must check keyword
        # Direct Text check (from STT transcript)
        if text:
            detected, keyword, stripped = self._detect_in_text(text)
            if detected:
                event = WakeWordEvent(
                    keyword=keyword,
                    detected=True,
                    confidence=0.98,
                    mode=WakeWordMode.WAKE_WORD_ONLY,
                )
                return True, stripped, event

        # Direct Audio ASCII / Heuristic check (for low-latency trigger)
        if audio_chunk:
            try:
                decoded = audio_chunk.decode("utf-8", errors="ignore").lower()
                for kw in self.keywords:
                    if kw in decoded:
                        event = WakeWordEvent(
                            keyword=kw,
                            detected=True,
                            confidence=0.90,
                            mode=WakeWordMode.WAKE_WORD_ONLY,
                        )
                        return True, text or "", event
            except Exception:
                pass

        return False, None, None

    def _detect_in_text(self, text: str) -> Tuple[bool, str, str]:
        """Detects if any configured wake-word appears at the start of the transcript."""
        clean = text.strip()
        lower = clean.lower()

        # Sort keywords longest first to match "hey nova" before "nova"
        sorted_kw = sorted(self.keywords, key=len, reverse=True)

        for kw in sorted_kw:
            # Check prefix match with word boundary
            pattern = rf"^(?:hey\s+)?{re.escape(kw)}[\s,:\.!-]*"
            match = re.match(pattern, lower)
            if match:
                end_pos = match.end()
                stripped = clean[end_pos:].strip()
                return True, kw, stripped

            # Also allow keyword anywhere in the first 3 words
            words = lower.split()
            if kw in words[:3]:
                # Remove keyword from text
                stripped = re.sub(rf"\b{re.escape(kw)}\b", "", clean, count=1, flags=re.IGNORECASE).strip()
                return True, kw, stripped

        return False, "", clean

    def _strip_wake_word_prefix(self, text: Optional[str]) -> str:
        """Safely removes wake word if present in followup speech."""
        if not text:
            return ""
        detected, _, stripped = self._detect_in_text(text)
        return stripped if detected else text

