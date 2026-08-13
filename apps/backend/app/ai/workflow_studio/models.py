"""Pydantic data models, enums, and schemas for Universal Workflow Learning & No-Code Automation Studio.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class WorkflowRecordingState(str, Enum):
    """Enumerate workflow recorder state machine states."""

    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"


class WorkflowTriggerType(str, Enum):
    """Enumerate workflow trigger event types."""

    VOICE = "voice"
    SCHEDULE = "schedule"
    FILE_CREATED = "file_created"
    FOLDER_CHANGED = "folder_changed"
    EMAIL_ARRIVED = "email_arrived"
    CLIPBOARD_CHANGED = "clipboard_changed"
    USB_INSERTED = "usb_inserted"
    APP_OPENED = "app_opened"
    WINDOW_APPEARED = "window_appeared"
    WEBHOOK = "webhook"
    API = "api"


class WorkflowActionType(str, Enum):
    """Enumerate workflow step action categories."""

    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    TYPE_TEXT = "type_text"
    PRESS_KEY = "press_key"
    HOTKEY = "hotkey"
    HOVER = "hover"
    SCROLL = "scroll"
    COPY_PASTE = "copy_paste"
    WAIT = "wait"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    HUMAN_APPROVAL = "human_approval"


class RecordedEvent(BaseModel):
    """Low-level input event captured during workflow recording."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str = Field(...)
    target_app: str = Field("Desktop")
    target_control: Optional[str] = Field(None)
    x: Optional[int] = Field(None)
    y: Optional[int] = Field(None)
    text_value: Optional[str] = Field(None)
    timestamp: float = Field(default_factory=time.time)


class WorkflowVariable(BaseModel):
    """Variable definition for dynamic workflow inputs and outputs."""

    var_id: str = Field(default_factory=lambda: f"var_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    var_type: str = Field("string")
    value: Any = Field(None)
    is_sensitive: bool = Field(False)
    description: str = Field("")


class WorkflowTrigger(BaseModel):
    """Trigger configuration payload."""

    trigger_id: str = Field(default_factory=lambda: f"trig_{uuid.uuid4().hex[:8]}")
    trigger_type: WorkflowTriggerType = Field(WorkflowTriggerType.VOICE)
    expression: str = Field("Hey Nova, run workflow")
    enabled: bool = Field(True)


class WorkflowStep(BaseModel):
    """High-level semantic workflow execution step."""

    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    action_type: WorkflowActionType = Field(WorkflowActionType.CLICK)
    description: str = Field(...)
    target_selector: str = Field("button#submit")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    condition_rule: Optional[str] = Field(None)
    timeout_sec: float = Field(30.0)


class WorkflowDefinition(BaseModel):
    """Complete structured workflow definition."""

    workflow_id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    description: str = Field("Learned workflow automation")
    steps: List[WorkflowStep] = Field(default_factory=list)
    variables: List[WorkflowVariable] = Field(default_factory=list)
    triggers: List[WorkflowTrigger] = Field(default_factory=list)
    version: str = Field("1.0.0")
    created_at: float = Field(default_factory=time.time)


class WorkflowExecutionResult(BaseModel):
    """Result payload after executing a workflow."""

    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    workflow_id: str = Field(...)
    success: bool = Field(True)
    steps_completed: int = Field(0)
    duration_sec: float = Field(0.0)
    error_message: Optional[str] = Field(None)
    timestamp: float = Field(default_factory=time.time)


class WorkflowStudioHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    total_workflows_count: int = Field(0)
    active_recordings_count: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class WorkflowStudioMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_recordings: int = Field(0)
    total_executions: int = Field(0)
    workflows_created: int = Field(0)
    variables_detected: int = Field(0)
    timestamp: float = Field(default_factory=time.time)
