"""Domain Models and State Enums for Nova-AI Conversational Voice Assistant (Phase 10M-B).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class VADState(str, Enum):
    """Voice Activity Detection state machine."""
    SILENCE = "silence"
    SPEECH_STARTED = "speech_started"
    SPEECH_ACTIVE = "speech_active"
    SPEECH_ENDED = "speech_ended"


class ConversationalState(str, Enum):
    """Lifecycle state of the conversational voice session."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    PLANNING = "planning"
    EXECUTING = "executing"
    SPEAKING = "speaking"
    AWAITING_FOLLOWUP = "awaiting_followup"
    MUTED = "muted"
    CANCELLED = "cancelled"
    ERROR = "error"


class WakeWordMode(str, Enum):
    """Wake-word activation mode."""
    WAKE_WORD_ONLY = "wake_word_only"
    PUSH_TO_TALK = "push_to_talk"
    CONTINUOUS_CONVERSATION = "continuous_conversation"


class SpeechIntentType(str, Enum):
    """Classified conversational intent category."""
    ACTIONABLE_COMMAND = "actionable_command"
    CHITCHAT_CONVERSATION = "chitchat_conversation"
    CLARIFICATION_ANSWER = "clarification_answer"
    SYSTEM_CONTROL = "system_control"
    INCOMPLETE = "incomplete"
    CORRECTION = "correction"


@dataclass
class AudioFrame:
    """Represents a single raw audio chunk with acoustic metadata."""
    data: bytes
    timestamp: float = field(default_factory=time.time)
    rms: float = 0.0
    energy_db: float = -100.0
    is_speech: bool = False
    zero_crossing_rate: float = 0.0


@dataclass
class WakeWordEvent:
    """Telemetry payload when wake word is detected."""
    keyword: str
    detected: bool
    confidence: float = 1.0
    mode: WakeWordMode = WakeWordMode.WAKE_WORD_ONLY
    timestamp: float = field(default_factory=time.time)


@dataclass
class SpeechAnalysisResult:
    """Result of speech intelligence decomposition."""
    raw_transcript: str
    cleaned_transcript: str
    intent_type: SpeechIntentType
    target_goal: str
    target_app: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_incomplete: bool = False
    missing_information_prompt: Optional[str] = None
    corrected_from: Optional[str] = None
    detected_language: str = "en"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_transcript": self.raw_transcript,
            "cleaned_transcript": self.cleaned_transcript,
            "intent_type": self.intent_type.value,
            "target_goal": self.target_goal,
            "target_app": self.target_app,
            "parameters": self.parameters,
            "is_incomplete": self.is_incomplete,
            "missing_information_prompt": self.missing_information_prompt,
            "corrected_from": self.corrected_from,
            "detected_language": self.detected_language,
            "confidence": self.confidence,
        }


@dataclass
class ConversationalVoiceTurn:
    """Single conversational turn in multi-turn spoken dialogue."""
    turn_id: str
    session_id: str
    user_transcript: str
    assistant_spoken_response: str
    intent_type: SpeechIntentType
    task_id: Optional[str] = None
    execution_success: bool = True
    tts_path: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "user_transcript": self.user_transcript,
            "assistant_spoken_response": self.assistant_spoken_response,
            "intent_type": self.intent_type.value,
            "task_id": self.task_id,
            "execution_success": self.execution_success,
            "tts_path": self.tts_path,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class MicrophoneStatus:
    """Current state of audio capture and privacy kill-switch."""
    is_active: bool = True
    is_muted: bool = False
    mode: WakeWordMode = WakeWordMode.WAKE_WORD_ONLY
    state: ConversationalState = ConversationalState.IDLE
    device_name: str = "Default Microphone"
    rms_level: float = 0.0
    db_level: float = -100.0
    frames_processed: int = 0
    privacy_indicator: str = "OFF"  # "OFF", "LISTENING", "PROCESSING", "MUTED"


@dataclass
class ConversationalSession:
    """Maintains multi-turn conversational voice session state."""
    session_id: str
    state: ConversationalState = ConversationalState.IDLE
    wake_word_mode: WakeWordMode = WakeWordMode.WAKE_WORD_ONLY
    mic_status: MicrophoneStatus = field(default_factory=MicrophoneStatus)
    active_task_id: Optional[str] = None
    active_app: Optional[str] = None
    turns: List[ConversationalVoiceTurn] = field(default_factory=list)
    last_interaction_time: float = field(default_factory=time.time)
    followup_window_sec: float = 6.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_in_followup_window(self) -> bool:
        """Returns True if session is within the continuous multi-turn window."""
        return (time.time() - self.last_interaction_time) <= self.followup_window_sec

    def add_turn(self, turn: ConversationalVoiceTurn) -> None:
        """Appends a turn and updates active timestamp."""
        self.turns.append(turn)
        self.last_interaction_time = time.time()

