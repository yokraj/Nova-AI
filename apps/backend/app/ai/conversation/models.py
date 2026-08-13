"""Pydantic data models, enums, and schemas for Conversation & Emotional Intelligence Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class EmotionState(str, Enum):
    """Enumerate user emotion states detected by the Emotion Engine."""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    STRESSED = "stressed"
    EXCITED = "excited"
    URGENT = "urgent"
    NEUTRAL = "neutral"
    BURNOUT = "burnout"


class PersonalityProfileType(str, Enum):
    """Enumerate AI conversational personality profiles."""

    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    DEVELOPER = "developer"
    TEACHER = "teacher"
    EXECUTIVE = "executive"
    RESEARCHER = "researcher"
    MINIMAL = "minimal"
    DETAILED = "detailed"
    CUSTOM = "custom"


class ConversationTurnRole(str, Enum):
    """Role associated with a conversational utterance turn."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationState(str, Enum):
    """Lifecycle state of an active conversation session."""

    ACTIVE = "active"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    STREAMING = "streaming"
    COMPLETED = "completed"
    EXPIRED = "expired"


class EmotionMetadata(BaseModel):
    """Descriptor model for detected emotion and voice adaptation settings."""

    primary_emotion: EmotionState = Field(EmotionState.NEUTRAL)
    confidence: float = Field(0.95)
    speech_rate_multiplier: float = Field(1.0)
    pitch_shift: float = Field(0.0)
    tone_descriptor: str = Field("balanced and attentive")


class PersonalityMetadata(BaseModel):
    """Descriptor model for an active personality profile."""

    profile_type: PersonalityProfileType = Field(PersonalityProfileType.DEVELOPER)
    name: str = Field("Developer Partner")
    tone: str = Field("technical, clear, and efficient")
    verbosity: str = Field("medium")
    technical_depth: str = Field("high")
    voice_id: str = Field("piper_en_developer")


class ConversationContextSnapshot(BaseModel):
    """Snapshot of desktop and cognitive context captured during turn execution."""

    active_app: str = Field("VS Code")
    active_project: str = Field("c:\\Projects\\Nova-AI")
    active_file: str = Field("main.py")
    browser_tab: str = Field("GitHub - Nova AI")
    mission_id: Optional[str] = Field(None)
    agent_role: str = Field("software_engineer")


class ConversationTurn(BaseModel):
    """Individual utterance turn within a conversation history."""

    turn_id: str = Field(default_factory=lambda: f"turn_{uuid.uuid4().hex[:8]}")
    role: ConversationTurnRole = Field(...)
    text: str = Field(...)
    emotion: EmotionMetadata = Field(default_factory=EmotionMetadata)
    timestamp: float = Field(default_factory=time.time)
    token_count: int = Field(15)
    context_snapshot: ConversationContextSnapshot = Field(default_factory=ConversationContextSnapshot)


class ClarificationOption(BaseModel):
    """Option payload for smart context-aware clarification prompts."""

    option_id: str = Field(...)
    label: str = Field(...)
    description: str = Field("")
    target_intent: str = Field("")


class ConversationSession(BaseModel):
    """Full multi-turn conversation session instance."""

    session_id: str = Field(default_factory=lambda: f"csess_{uuid.uuid4().hex[:8]}")
    user_id: str = Field("user_primary")
    personality: PersonalityMetadata = Field(default_factory=PersonalityMetadata)
    turns: List[ConversationTurn] = Field(default_factory=list)
    current_state: ConversationState = Field(ConversationState.ACTIVE)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class ConversationResponsePayload(BaseModel):
    """Result payload returned by conversation engine execution."""

    session_id: str = Field(...)
    text_response: str = Field(...)
    audio_output_path: Optional[str] = Field(None)
    emotion: EmotionMetadata = Field(default_factory=EmotionMetadata)
    personality: PersonalityMetadata = Field(default_factory=PersonalityMetadata)
    latency_ms: float = Field(45.0)
    clarification_options: List[ClarificationOption] = Field(default_factory=list)


class ConversationHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    active_sessions_count: int = Field(0)
    total_turns_processed: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class ConversationMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_conversations: int = Field(0)
    total_turns: int = Field(0)
    emotions_detected: int = Field(0)
    interruptions_handled: int = Field(0)
    avg_latency_ms: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)
