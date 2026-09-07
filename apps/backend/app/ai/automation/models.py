"""Domain models and data schemas for Native Desktop & Browser Automation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AutomationState(str, Enum):
    """Lifecycle state of an automation execution."""

    IDLE = "idle"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionType(str, Enum):
    """Categories of automation actions."""

    DESKTOP = "desktop"
    BROWSER = "browser"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    CLIPBOARD = "clipboard"
    WINDOW = "window"
    PROCESS = "process"
    OCR = "ocr"
    FORM = "form"


class BrowserType(str, Enum):
    """Supported browser engines."""

    CHROME = "chrome"
    EDGE = "edge"
    FIREFOX = "firefox"


class TargetPlatform(str, Enum):
    """Operating system platform target."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


class WindowAction(str, Enum):
    """Window management actions."""

    FOCUS = "focus"
    MOVE = "move"
    RESIZE = "resize"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    CLOSE = "close"


# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

class UIElement(BaseModel):
    """UI element bounding box and metadata on screen or page."""

    element_id: str = Field(default_factory=lambda: f"elem_{uuid4().hex[:8]}")
    name: str = ""
    tag_name: str = ""
    role: str = ""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    text: str = ""
    is_interactive: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class WindowInfo(BaseModel):
    """Specification of an open desktop application window."""

    handle: int = 0
    title: str = ""
    process_name: str = ""
    pid: int = 0
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    is_active: bool = False
    is_minimized: bool = False
    is_maximized: bool = False


class ProcessInfo(BaseModel):
    """Process execution information."""

    pid: int
    name: str
    executable_path: str = ""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0


class OCRResult(BaseModel):
    """Extracted text bounding box from screen, image, or PDF."""

    text: str
    confidence: float = 1.0
    bounding_box: Dict[str, int] = Field(default_factory=dict)
    lines: List[str] = Field(default_factory=list)


class ImageMatch(BaseModel):
    """Template image match location on screen."""

    found: bool
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    confidence: float = 0.0


class AutomationRequest(BaseModel):
    """Request invocation for desktop or browser automation."""

    request_id: str = Field(default_factory=lambda: f"auto_req_{uuid4().hex[:10]}")
    action_type: ActionType
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "system"
    mission_id: Optional[str] = None
    timeout_seconds: float = 60.0


class AutomationResult(BaseModel):
    """Output result of an automation request."""

    request_id: str
    action_name: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    human_approved: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AutomationMetrics(BaseModel):
    """Telemetry metrics snapshot for the automation engine."""

    total_automations: int = 0
    successful_automations: int = 0
    failed_automations: int = 0
    success_rate: float = 0.0
    average_duration_seconds: float = 0.0
    desktop_actions_count: int = 0
    browser_actions_count: int = 0
    ocr_extractions_count: int = 0
    form_fills_count: int = 0


class AutomationHealth(BaseModel):
    """Composite health state of the automation engine."""

    status: str = "healthy"
    components: Dict[str, str] = Field(default_factory=dict)
    active_browser_sessions: int = 0
    open_windows_count: int = 0


class SafetyReport(BaseModel):
    """Safety evaluation report for automation actions."""

    is_safe: bool = True
    risk_level: str = "low"
    reasons: List[str] = Field(default_factory=list)
    requires_approval: bool = False


class MouseAction(BaseModel):
    """Mouse interaction payload."""

    action: str = Field("click")
    x: int = Field(0)
    y: int = Field(0)
    button: str = Field("left")
    clicks: int = Field(1)


class KeyboardAction(BaseModel):
    """Keyboard interaction payload."""

    action: str = Field("type")
    text: str = Field("")
    key: str = Field("")


class RollbackStep(BaseModel):
    """Single action rollback step definition."""

    step_id: str = Field(default_factory=lambda: f"rb_{uuid4().hex[:8]}")
    action_name: str = Field("")
    undo_action: str = Field("")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RollbackPlan(BaseModel):
    """Composite execution rollback plan."""

    plan_id: str = Field(default_factory=lambda: f"plan_{uuid4().hex[:8]}")
    steps: List[RollbackStep] = Field(default_factory=list)



AutomationResponse = AutomationResult
ExecutionResult = AutomationResult
ActionStep = AutomationRequest



