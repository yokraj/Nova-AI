"""Pydantic V2 data models and schemas for Always-On Voice Runtime & Continuous Cognitive Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class OSState(str, Enum):
    """Enumerate operating system background lifecycle states."""

    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    IDLE = "IDLE"
    PAUSED = "PAUSED"
    RESTARTING = "RESTARTING"
    SAFE_MODE = "SAFE_MODE"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    SHUTTING_DOWN = "SHUTTING_DOWN"


class SubsystemStatus(str, Enum):
    """Subsystem operational status."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRASHED = "CRASHED"
    RECOVERING = "RECOVERING"
    STOPPED = "STOPPED"


class VoiceUserRole(str, Enum):
    """User authentication role identified by voice print."""

    OWNER = "OWNER"
    ADMINISTRATOR = "ADMINISTRATOR"
    ENTERPRISE_USER = "ENTERPRISE_USER"
    GUEST = "GUEST"
    UNKNOWN = "UNKNOWN"


class VADState(str, Enum):
    """Voice Activity Detector states."""

    SILENCE = "SILENCE"
    START_OF_SPEECH = "START_OF_SPEECH"
    SPEECH_IN_PROGRESS = "SPEECH_IN_PROGRESS"
    END_OF_SPEECH = "END_OF_SPEECH"


# Backward Compatible M3.4.16 Models
class OSDashboardState(BaseModel):
    """OS Administrative Dashboard state."""

    os_state: OSState = Field(OSState.RUNNING)
    active_agents: List[str] = Field(default_factory=lambda: ["Architect", "Backend", "VoiceWorkforce"])
    active_models: List[str] = Field(default_factory=lambda: ["qwen3:8b", "whisper-large-v3"])
    cpu_percent: float = Field(2.5)
    ram_percent: float = Field(15.0)
    health_score: float = Field(100.0)


class NotificationPayload(BaseModel):
    """System notification payload."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(...)
    message: str = Field(...)


class OSMetrics(BaseModel):
    """OS Telemetry Metrics."""

    cpu_usage: float = Field(2.5)
    memory_usage_mb: float = Field(512.0)
    uptime_seconds: float = Field(3600.0)


class OSSecurityPolicy(BaseModel):
    """OS Security Policy rules."""

    policy_name: str = Field("default_strict")
    enforce_voice_auth: bool = Field(True)
    enforce_approval_holds: bool = Field(True)


class OSSession(BaseModel):
    """OS Session descriptor."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user: str = Field("owner")
    user_id: str = Field("owner@nova-ai.org")
    active_workspace: str = Field("Default Workspace")



class SchedulerJob(BaseModel):
    """OS Unified Scheduler Job."""

    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:8]}")

    name: str = Field(...)
    status: str = Field("RUNNING")


class SystemEvent(BaseModel):
    """System Event structure."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


# M3.4.19 Models
class OSBootDiagnostic(BaseModel):
    """Diagnostic details logged during OS boot sequence."""

    subsystem_id: str = Field("os_core_subsystem")
    boot_id: str = Field(default_factory=lambda: f"boot_{uuid.uuid4().hex[:8]}")
    boot_duration_ms: float = Field(0.0)
    duration_sec: float = Field(0.0)
    subsystems_loaded: List[str] = Field(default_factory=list)
    success: bool = Field(True)
    status: SubsystemStatus = Field(SubsystemStatus.HEALTHY)
    error_message: Optional[str] = Field(None)


class WakeWordDetection(BaseModel):
    """Wake-word detection event details."""

    detected: bool = Field(True)
    phrase: str = Field("Hey Nova")
    confidence: float = Field(0.96)
    timestamp: float = Field(default_factory=time.time)


class VoicePrintVerification(BaseModel):
    """Voice print authentication result."""

    verified: bool = Field(True)
    user_id: str = Field("owner_primary")
    role: VoiceUserRole = Field(VoiceUserRole.OWNER)
    confidence: float = Field(0.94)


class PartialTranscript(BaseModel):
    """Real-time streaming speech recognition partial output."""

    transcript: str = Field(...)
    is_final: bool = Field(False)
    confidence: float = Field(0.92)
    language: str = Field("en")


class EarlyReasoningResult(BaseModel):
    """Speculative reasoning outcome calculated on partial transcript."""

    partial_intent: str = Field(...)
    speculative_action: str = Field(...)
    ready_for_execution: bool = Field(False)


class ConfirmationHold(BaseModel):
    """Confirmation hold request for sensitive operations."""

    hold_id: str = Field(default_factory=lambda: f"hold_{uuid.uuid4().hex[:8]}")
    action_type: str = Field(...)
    description: str = Field(...)
    risk_level: str = Field("HIGH")
    confirmed: bool = Field(False)
    timestamp: float = Field(default_factory=time.time)


class ProactiveVoiceNotification(BaseModel):
    """Proactive voice alert payload."""

    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    message: str = Field(...)
    category: str = Field("info")
    spoken: bool = Field(False)
    timestamp: float = Field(default_factory=time.time)


class SystemTrayStatus(BaseModel):
    """Windows System Tray status snapshot."""

    icon_state: str = Field("active")
    microphone_muted: bool = Field(False)
    listening_active: bool = Field(True)
    active_models_count: int = Field(3)
    active_mission_name: Optional[str] = Field(None)


class VoiceAgentBlueprint(BaseModel):
    """Voice agent metadata within the 15-agent Voice Workforce."""

    agent_id: str = Field(...)
    name: str = Field(...)
    role: str = Field(...)
    is_active: bool = Field(True)


class MissionCheckpoint(BaseModel):
    """Long-running background mission state snapshot."""

    mission_id: str = Field(...)
    name: str = Field(...)
    progress_percent: float = Field(0.0)
    current_step: str = Field(...)
    checkpoint_timestamp: float = Field(default_factory=time.time)


class OSHealth(BaseModel):
    """Overall OS background runtime health metrics."""

    is_healthy: bool = Field(True)
    os_state: OSState = Field(OSState.RUNNING)
    health_score: float = Field(100.0)
    active_subsystems_count: int = Field(25)
    cpu_percent: float = Field(2.5)
    ram_used_mb: float = Field(512.0)
    vram_used_mb: float = Field(1024.0)
    timestamp: float = Field(default_factory=time.time)
