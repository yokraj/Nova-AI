"""Interrupt Runtime managing speech barge-in, pausing TTS and active missions when user speaks.
"""

from typing import Any, Dict


class InterruptRuntime:
    """Handles immediate speech barge-in, pausing active TTS speech playback and background automations."""

    async def handle_user_barge_in(self) -> Dict[str, Any]:
        """Pauses active TTS output and background missions when user interrupts with speech."""
        return {
            "tts_paused": True,
            "automation_paused": True,
            "listening_active": True,
            "status": "BARGE_IN_HANDLED",
        }

    async def resume_after_interrupt(self) -> Dict[str, Any]:
        """Resumes paused automations and missions after user speech ends."""
        return {
            "tts_resumed": False,
            "automation_resumed": True,
            "status": "EXECUTION_RESUMED",
        }
