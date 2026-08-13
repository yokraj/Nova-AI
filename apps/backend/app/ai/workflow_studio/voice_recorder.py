"""Voice Recorder capturing spoken voice narration and spoken action overlays.
"""

from app.ai.workflow_studio.models import RecordedEvent


class VoiceRecorder:
    """Captures user voice narration overlaid during workflow recording."""

    def capture_narration(self, transcript: str) -> RecordedEvent:
        """Captures voice narration event."""
        return RecordedEvent(
            event_type="voice_narration",
            target_app="VoiceEngine",
            text_value=transcript,
        )
