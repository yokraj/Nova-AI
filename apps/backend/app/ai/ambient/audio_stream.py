"""Audio Stream buffering PCM frames for speech pipelines."""

from collections import deque
from typing import List, Optional
import structlog

from app.ai.ambient.models import AudioFrame

logger = structlog.get_logger("audio_stream")


class AudioStream:
    """In-memory ring buffer for streaming audio frames."""

    def __init__(self, maxlen: int = 100) -> None:
        self.buffer: deque[AudioFrame] = deque(maxlen=maxlen)

    def push_frame(self, frame: AudioFrame) -> None:
        """Push audio frame into ring buffer."""
        self.buffer.append(frame)

    def get_recent_frames(self, count: int = 10) -> List[AudioFrame]:
        """Retrieve recent audio frames."""
        return list(self.buffer)[-count:]
