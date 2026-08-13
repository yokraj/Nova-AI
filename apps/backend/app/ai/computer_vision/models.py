"""Pydantic data models, enums, and structures for Computer Vision & GUI Intelligence.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ElementType(str, Enum):
    """Enumerate GUI element classifications."""

    BUTTON = "button"
    TEXT_FIELD = "text_field"
    MENU = "menu"
    DIALOG = "dialog"
    TOOLBAR = "toolbar"
    STATUS_BAR = "status_bar"
    TASKBAR = "taskbar"
    SYSTEM_TRAY = "system_tray"
    ICON = "icon"
    TAB = "tab"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    GRID = "grid"
    IMAGE = "image"
    UNKNOWN = "unknown"


class ReasoningPurpose(str, Enum):
    """Enumerate visual reasoning purposes."""

    AUTOMATION_RECOVERY = "automation_recovery"
    LOCATE_CONTROL = "locate_control"
    ERROR_DIAGNOSIS = "error_diagnosis"
    DOCUMENT_EXTRACTION = "document_extraction"
    ACTION_GUIDANCE = "action_guidance"


class VisionState(str, Enum):
    """Enumerate state of Computer Vision Engine."""

    IDLE = "IDLE"
    CAPTURING = "CAPTURING"
    ANALYZING = "ANALYZING"
    LOCATING = "LOCATING"
    REASONING = "REASONING"
    RECOVERING = "RECOVERING"
    ERROR = "ERROR"
    PAUSED = "PAUSED"


class GUIElement(BaseModel):
    """Single detected UI element descriptor."""

    element_id: str = Field(default_factory=lambda: f"elem_{uuid.uuid4().hex[:8]}")
    type: ElementType = Field(ElementType.BUTTON)
    label: str = Field("", description="Visible label or accessible name")
    confidence: float = Field(0.9, description="Confidence score 0.0 to 1.0")
    bounding_box: Dict[str, int] = Field(
        default_factory=lambda: {"x": 0, "y": 0, "width": 100, "height": 30}
    )
    is_interactive: bool = Field(True)
    is_visible: bool = Field(True)
    accessibility_id: Optional[str] = Field(None)
    xpath: Optional[str] = Field(None)
    text_content: Optional[str] = Field(None)


class DesktopScene(BaseModel):
    """Structured scene representation of current desktop."""

    scene_id: str = Field(default_factory=lambda: f"scne_{uuid.uuid4().hex[:8]}")
    active_window_title: str = Field("Desktop")
    process_name: str = Field("explorer.exe")
    resolution: Dict[str, int] = Field(default_factory=lambda: {"width": 1920, "height": 1080})
    monitor_index: int = Field(0)
    hierarchy: Dict[str, Any] = Field(default_factory=dict)
    elements: List[GUIElement] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class VisualReasoningResult(BaseModel):
    """Result of visual reasoning over a screenshot or screen element."""

    reasoning_id: str = Field(default_factory=lambda: f"reas_{uuid.uuid4().hex[:8]}")
    purpose: ReasoningPurpose = Field(ReasoningPurpose.AUTOMATION_RECOVERY)
    diagnosis: str = Field(...)
    recommended_action: str = Field(...)
    target_element: Optional[GUIElement] = Field(None)
    confidence: float = Field(0.9)
    recovery_steps: List[str] = Field(default_factory=list)


class ApplicationProfile(BaseModel):
    """Application layout and workflow profile."""

    app_name: str = Field(...)
    process_names: List[str] = Field(default_factory=list)
    common_ui_regions: Dict[str, Any] = Field(default_factory=dict)
    known_menus: List[str] = Field(default_factory=list)
    expected_workflows: List[str] = Field(default_factory=list)
    known_dialogs: List[str] = Field(default_factory=list)


class AdaptiveLocatorResult(BaseModel):
    """Adaptive UI control locator match result."""

    found: bool = Field(True)
    element: Optional[GUIElement] = Field(None)
    locator_strategy: str = Field("accessibility_api", description="Strategy used (accessibility_api, dom, ocr, visual_similarity)")
    confidence: float = Field(0.95)
    matches_count: int = Field(1)
    execution_time_ms: float = Field(5.0)


class DocumentStructure(BaseModel):
    """Structured output from OCR and document understanding."""

    doc_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    title: str = Field("")
    page_count: int = Field(1)
    paragraphs: List[str] = Field(default_factory=list)
    tables: List[List[List[str]]] = Field(default_factory=list)
    forms: Dict[str, str] = Field(default_factory=dict)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    extracted_text: str = Field("")


class IDEScene(BaseModel):
    """IDE workspace layout snapshot for AI Software Copilot."""

    scene_id: str = Field(default_factory=lambda: f"ide_{uuid.uuid4().hex[:8]}")
    active_file: str = Field("main.py")
    project_path: str = Field("c:\\Projects\\Nova-AI")
    open_tabs: List[str] = Field(default_factory=list)
    cursor_line: int = Field(1)
    cursor_col: int = Field(1)
    errors_count: int = Field(0)
    warnings_count: int = Field(0)
    git_status: str = Field("clean")
    terminal_output: str = Field("")


class BrowserScene(BaseModel):
    """Browser web page layout snapshot."""

    scene_id: str = Field(default_factory=lambda: f"web_{uuid.uuid4().hex[:8]}")
    page_title: str = Field("")
    url: str = Field("")
    page_purpose: str = Field("general_browsing")
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    is_checkout: bool = Field(False)
    is_login: bool = Field(False)
    active_alerts: List[str] = Field(default_factory=list)


class RecoveryPlan(BaseModel):
    """Automated GUI automation recovery plan."""

    plan_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    failure_reason: str = Field(...)
    original_target: str = Field(...)
    alternative_element: Optional[GUIElement] = Field(None)
    recovery_action: str = Field(...)
    verified: bool = Field(True)


class ScreenHistoryItem(BaseModel):
    """Historical screen memory record."""

    history_id: str = Field(default_factory=lambda: f"hist_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    window_title: str = Field("")
    process_name: str = Field("")
    screenshot_hash: str = Field("")
    action_taken: Optional[str] = Field(None)


class VisionMetrics(BaseModel):
    """Telemetry collector metrics model."""

    screens_analyzed: int = Field(0)
    elements_located: int = Field(0)
    ocr_operations: int = Field(0)
    recoveries_attempted: int = Field(0)
    average_latency_ms: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class VisionHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    vision_state: VisionState = Field(VisionState.IDLE)
    active_monitors_count: int = Field(1)
    loaded_profiles: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
