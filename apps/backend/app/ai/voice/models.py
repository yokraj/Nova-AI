"""Domain models and schemas for the Enterprise Voice Intelligence Layer.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class VoiceRequest(BaseModel):
    """Voice request input containing target audio sources."""
    audio_path: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    session_id: Optional[UUID] = None
    language: str = "en"

class VoiceResponse(BaseModel):
    """Voice execution response containing transcripts and generated audio file paths."""
    text: str
    audio_path: Optional[str] = None
    confidence: float = 1.0
    processing_time: float = 0.0

class SpeechResult(BaseModel):
    """Outcome of Speech-To-Text transcription processes."""
    transcript: str
    confidence: float
    language: str

class VoiceSession(BaseModel):
    """Tracks state and life details for an active voice listener stream."""
    id: UUID = Field(default_factory=uuid4)
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    status: str = "active"

class VoiceCommand(BaseModel):
    """Parsed voice intent descriptor."""
    command_type: str
    intent: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
