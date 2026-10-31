"""Data models and type definitions for Nova-AI Unified Multimodal Orchestration (Phase 10M-A).

Unifies text, voice, vision, and desktop context into structured interaction payloads.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field as PydanticField


class InputModality(str, Enum):
    """Supported input modalities for Nova multimodal interaction."""

    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    SCREENSHOT = "screenshot"
    MIXED = "mixed"


class InteractionState(str, Enum):
    """Lifecycle states of a multimodal interaction."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    SPEAKING = "speaking"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class IntentCategory(str, Enum):
    """Classified intent categories for multimodal commands."""

    DESKTOP_ACTION = "desktop_action"
    APPLICATION_CONTROL = "application_control"
    WORKFLOW_AUTOMATION = "workflow_automation"
    RESEARCH_QUERY = "research_query"
    CONVERSATION = "conversation"
    CLARIFICATION_ANSWER = "clarification_answer"
    CANCEL_ACTION = "cancel_action"
    UNKNOWN = "unknown"


class ScreenReference(BaseModel):
    """Visual or deictic reference grounded in screen content."""

    reference_text: str = PydanticField(..., description="Original user text reference, e.g. 'this button'")
    target_type: str = PydanticField("ui_element", description="Type: window, button, input, menu, region")
    resolved_label: Optional[str] = PydanticField(None, description="Resolved control label or title")
    bounding_box: Optional[Dict[str, int]] = PydanticField(None, description="Screen coordinates {x, y, width, height}")
    confidence: float = PydanticField(1.0, description="Detection / grounding confidence (0.0 to 1.0)")
    is_uncertain: bool = PydanticField(False, description="True if visual grounding is ambiguous or below safety threshold")


class ActiveAppContext(BaseModel):
    """Real-time active window and desktop application context."""

    app_name: str = PydanticField("System", description="Target application name (e.g. Blender, VS Code)")
    window_title: str = PydanticField("", description="Active foreground window title")
    window_handle: str = PydanticField("0x0", description="OS window handle")
    process_id: int = PydanticField(0, description="OS process identifier")
    process_name: str = PydanticField("", description="Process executable name")
    is_foreground: bool = PydanticField(True, description="Whether this window holds foreground input focus")


class ClarificationOption(BaseModel):
    """Individual option for resolving ambiguous user requests."""

    option_id: str = PydanticField(..., description="Unique option key (e.g. 'opt_1')")
    label: str = PydanticField(..., description="Human-readable label for option")
    description: str = PydanticField("", description="Explanatory description")
    target_intent: Optional[str] = PydanticField(None, description="Underlying intent if chosen")
    resolved_parameters: Dict[str, Any] = PydanticField(default_factory=dict, description="Pre-filled parameters")


class ClarificationRequest(BaseModel):
    """Structured request for user clarification when essential information is missing."""

    clarification_id: str = PydanticField(default_factory=lambda: f"clar_{uuid.uuid4().hex[:8]}")
    prompt: str = PydanticField(..., description="Spoken/displayed clarification question")
    question: str = PydanticField(..., description="Summary question for display")
    options: List[ClarificationOption] = PydanticField(default_factory=list, description="Available choices")
    missing_parameter: Optional[str] = PydanticField(None, description="Name of the missing essential parameter")
    reason: str = PydanticField("", description="Why clarification is necessary")


class NormalizedMultimodalInput(BaseModel):
    """Unified normalized multimodal input representation."""

    input_id: str = PydanticField(default_factory=lambda: f"in_{uuid.uuid4().hex[:8]}")
    modality: InputModality
    raw_text: Optional[str] = None
    transcribed_text: Optional[str] = None
    effective_text: str = PydanticField(..., description="Canonical text prompt for semantic reasoning")
    audio_bytes: Optional[bytes] = None
    image_path: Optional[str] = None
    image_bytes: Optional[bytes] = None
    screenshot_active: bool = False
    active_app: Optional[ActiveAppContext] = None
    visual_ocr_text: Optional[str] = None
    session_id: str = PydanticField(default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}")
    requires_approval: bool = False
    timestamp: float = PydanticField(default_factory=time.time)


class StructuredTaskRequest(BaseModel):
    """Structured task request extracted from multimodal input for canonical execution."""

    request_id: str = PydanticField(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    intent_category: IntentCategory
    primary_goal: str
    target_app: str = "System"
    action_type: str = "general_action"
    parameters: Dict[str, Any] = PydanticField(default_factory=dict)
    entities: Dict[str, Any] = PydanticField(default_factory=dict)
    constraints: List[str] = PydanticField(default_factory=list)
    screen_references: List[ScreenReference] = PydanticField(default_factory=list)
    required_permissions: List[str] = PydanticField(default_factory=list)
    requires_user_approval: bool = False
    needs_clarification: bool = False
    clarification_request: Optional[ClarificationRequest] = None
    confidence: float = 1.0
    visual_uncertainty: bool = False
    uncertainty_reason: Optional[str] = None


class MultimodalTurn(BaseModel):
    """Record of a single interaction turn within a task session."""

    turn_id: str = PydanticField(default_factory=lambda: f"turn_{uuid.uuid4().hex[:8]}")
    timestamp: float = PydanticField(default_factory=time.time)
    modality: InputModality
    user_text: str
    task_request: Optional[StructuredTaskRequest] = None
    status: str = "completed"
    agent_response_text: str = ""
    tts_audio_path: Optional[str] = None


class MultimodalConversationContext(BaseModel):
    """Task-specific conversation context maintaining state across multiple turns."""

    session_id: str
    active_task_id: Optional[str] = None
    active_app: Optional[str] = None
    turns: List[MultimodalTurn] = PydanticField(default_factory=list)
    pending_clarification: Optional[ClarificationRequest] = None
    last_task_request: Optional[StructuredTaskRequest] = None
    state: InteractionState = InteractionState.IDLE


class MultimodalExecutionResult(BaseModel):
    """Comprehensive result of multimodal interaction and canonical execution."""

    session_id: str
    task_id: str
    state: InteractionState
    success: bool
    spoken_response: str
    tts_audio_path: Optional[str] = None
    structured_request: StructuredTaskRequest
    task_graph_result: Optional[Dict[str, Any]] = None
    goal_verification: Optional[Dict[str, Any]] = None
    critic_result: Optional[Dict[str, Any]] = None
    approval_required: bool = False
    visual_uncertainty: bool = False
    clarification: Optional[ClarificationRequest] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
