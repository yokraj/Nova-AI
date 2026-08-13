"""Domain models and data schemas for Ambient Intelligence & Continuous Voice Assistant."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AmbientState(str, Enum):
    """Overall state of Ambient Engine."""

    IDLE = "idle"
    LISTENING = "listening"
    WAKE_WORD_DETECTED = "wake_word_detected"
    PROCESSING_SPEECH = "processing_speech"
    CONVERSING = "conversing"
    PAUSED = "paused"
    PRIVACY_MODE = "privacy_mode"


class WakeWordType(str, Enum):
    """Category of wake word detected."""

    PRIMARY = "primary"  # "Hey Nova"
    SHORT = "short"      # "Nova"
    CUSTOM = "custom"    # User custom phrase


class InterruptionPolicy(str, Enum):
    """Interruption gating policy during active user states."""

    ALWAYS = "always"
    LOW_INTERRUPTION = "low_interruption"
    DO_NOT_DISTURB = "do_not_disturb"
    NEVER = "never"


class PrivacyLevel(str, Enum):
    """User privacy operational level."""

    STANDARD = "standard"
    PAUSED = "paused"
    PRIVACY_ONLY = "privacy_only"
    INCOGNITO = "incognito"


class ConversationState(str, Enum):
    """Multi-turn conversation state."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    WAITING_USER = "waiting_user"
    COMPLETED = "completed"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class AudioFrame(BaseModel):
    """Chunk of PCM audio captured from continuous microphone listener."""

    frame_id: str = Field(default_factory=lambda: f"frm_{uuid4().hex[:8]}")
    data_bytes: bytes = b""
    sample_rate: int = 16000
    channels: int = 1
    has_speech: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WakeWordMatch(BaseModel):
    """Record of a successful wake word match."""

    match_id: str = Field(default_factory=lambda: f"ww_{uuid4().hex[:8]}")
    phrase: str
    confidence: float = 0.95
    wake_type: WakeWordType = WakeWordType.PRIMARY
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ActiveWindowInfo(BaseModel):
    """Focused active window details."""

    title: str = "VS Code - Nova AI Project"
    process_name: str = "Code.exe"
    is_meeting_app: bool = False
    is_ide: bool = True
    is_browser: bool = False


class ClipboardContent(BaseModel):
    """Captured clipboard text snapshot."""

    text: str = ""
    is_error_log: bool = False
    is_url: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationEvent(BaseModel):
    """Desktop notification event."""

    source: str
    title: str
    message: str
    is_low_battery: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DesktopContextSnapshot(BaseModel):
    """Composite snapshot of desktop awareness."""

    active_window: ActiveWindowInfo = Field(default_factory=ActiveWindowInfo)
    clipboard: ClipboardContent = Field(default_factory=ClipboardContent)
    notifications: List[NotificationEvent] = Field(default_factory=list)
    is_user_idle: bool = False
    is_in_meeting: bool = False
    uncommitted_changes: bool = False
    debugging_duration_minutes: float = 0.0


class ProactiveSuggestion(BaseModel):
    """Proactive ambient suggestion offered to user."""

    suggestion_id: str = Field(default_factory=lambda: f"sug_{uuid4().hex[:8]}")
    category: str  # meeting, debugging, git, battery, idle, form
    title: str
    message: str
    recommended_action: str = ""
    auto_create_mission: bool = False


class ConversationTurn(BaseModel):
    """Single turn in a multi-turn voice conversation."""

    turn_id: str = Field(default_factory=lambda: f"turn_{uuid4().hex[:8]}")
    speaker: str  # user, assistant
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoiceSessionRecord(BaseModel):
    """Active or historical voice session."""

    session_id: str = Field(default_factory=lambda: f"vses_{uuid4().hex[:8]}")
    state: ConversationState = ConversationState.ACTIVE
    turns: List[ConversationTurn] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)


class AmbientMetrics(BaseModel):
    """Telemetry metrics for Ambient Intelligence Engine."""

    audio_frames_processed: int = 0
    wake_words_detected: int = 0
    conversations_handled: int = 0
    proactive_suggestions_issued: int = 0
    missions_auto_created: int = 0
    privacy_toggles_count: int = 0


class AmbientHealth(BaseModel):
    """Composite health report for Ambient Engine."""

    status: str = "healthy"
    microphone_active: bool = True
    privacy_mode: bool = False
    monitors_online: Dict[str, str] = Field(default_factory=dict)
