"""Pydantic V2 data models, enums, and schemas for Universal Desktop, Browser & OS Automation Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class AutomationPriority(str, Enum):
    """Enumerate automation task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ExecutionMode(str, Enum):
    """Enumerate automation execution modes."""

    INTERACTIVE = "interactive"
    BACKGROUND = "background"
    SILENT = "silent"
    SIMULATION = "simulation"


class PermissionLevel(str, Enum):
    """Enumerate execution permission privilege levels."""

    USER = "user"
    ELEVATED = "elevated"
    ADMINISTRATOR = "administrator"
    SYSTEM = "system"


class ActionStatus(str, Enum):
    """Enumerate action execution status lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"
    RECOVERED = "recovered"
    WAITING_APPROVAL = "waiting_approval"


class DesktopSession(BaseModel):
    """Desktop session context payload."""

    session_id: str = Field(default_factory=lambda: f"dsess_{uuid.uuid4().hex[:8]}")
    user_id: str = Field("owner@nova-ai.org")
    active_desktop: str = Field("Desktop 1")
    monitor_count: int = Field(1)
    scaling_factor: float = Field(1.0)
    created_at: float = Field(default_factory=time.time)


class ApplicationInfo(BaseModel):
    """Desktop application process payload."""

    app_id: str = Field(default_factory=lambda: f"app_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    process_id: int = Field(0)
    executable_path: str = Field("")
    window_handle: str = Field("")
    is_running: bool = Field(True)


class WindowInfo(BaseModel):
    """Desktop window metadata payload."""

    window_id: str = Field(default_factory=lambda: f"win_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    class_name: str = Field("")
    process_id: int = Field(0)
    bounds: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "width": 1920, "height": 1080})
    is_active: bool = Field(True)
    is_minimized: bool = Field(False)
    is_maximized: bool = Field(True)


class BrowserSession(BaseModel):
    """Browser instance session metadata payload."""

    session_id: str = Field(default_factory=lambda: f"bsess_{uuid.uuid4().hex[:8]}")
    browser_name: str = Field("chrome")
    profile_path: str = Field("")
    is_incognito: bool = Field(False)
    active_tabs_count: int = Field(1)


class BrowserTab(BaseModel):
    """Browser tab metadata payload."""

    tab_id: str = Field(default_factory=lambda: f"tab_{uuid.uuid4().hex[:8]}")
    title: str = Field(...)
    url: str = Field("https://google.com")
    is_active: bool = Field(True)
    index: int = Field(0)


class ClipboardData(BaseModel):
    """System clipboard payload."""

    data_type: str = Field("text")
    text_content: Optional[str] = Field(None)
    image_bytes: Optional[bytes] = Field(None)
    files_list: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class MouseAction(BaseModel):
    """Mouse input action payload."""

    action_type: str = Field("click")
    x: int = Field(0)
    y: int = Field(0)
    button: str = Field("left")
    scroll_delta: int = Field(0)
    speed_multiplier: float = Field(1.0)


class KeyboardAction(BaseModel):
    """Keyboard input action payload."""

    action_type: str = Field("type_text")
    text: Optional[str] = Field(None)
    key_code: Optional[str] = Field(None)
    modifiers: List[str] = Field(default_factory=list)
    delay_ms: int = Field(50)


class DesktopCommand(BaseModel):
    """High-level desktop automation command payload."""

    command_id: str = Field(default_factory=lambda: f"cmd_{uuid.uuid4().hex[:8]}")
    name: str = Field(...)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: AutomationPriority = Field(AutomationPriority.NORMAL)


class AutomationAction(BaseModel):
    """Individual GUI or OS action step payload."""

    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}")
    action_type: str = Field("click")
    target_label: str = Field(default="")
    selector: Dict[str, Any] = Field(default_factory=dict)
    value: Optional[Any] = Field(None)
    timeout_sec: float = Field(10.0)

    @property
    def parameters(self) -> Dict[str, Any]:
        """Accessor property returning selector parameters or value dict."""
        if isinstance(self.selector, dict) and self.selector:
            return self.selector
        if self.value is not None:
            return {"value": self.value}
        return {}


class AutomationResult(BaseModel):
    """Outcome payload of executed automation action."""

    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    action_id: str = Field(...)
    success: bool = Field(True)
    output: Any = Field(None)
    error_message: Optional[str] = Field(None)
    duration_sec: float = Field(0.0)
    timestamp: float = Field(default_factory=time.time)


class VerificationResult(BaseModel):
    """Verification outcome payload confirming step success."""

    action_id: str = Field(...)
    verified: bool = Field(True)
    method_used: str = Field("accessibility_api")
    confidence: float = Field(0.98)
    details: str = Field("Control state verified successfully.")


class RecoveryPlan(BaseModel):
    """Recovery strategy payload for handling UI failures."""

    failure_reason: str = Field(...)
    recovery_strategy: str = Field("visual_locator_fallback")
    retry_recommended: bool = Field(True)
    steps: List[Dict[str, Any]] = Field(default_factory=list)


class ApplicationProfile(BaseModel):
    """Profile blueprint for desktop applications."""

    profile_id: str = Field(default_factory=lambda: f"prof_{uuid.uuid4().hex[:8]}")
    app_name: str = Field(...)
    executable_name: str = Field(...)
    main_window_title: str = Field("")
    control_map: Dict[str, Any] = Field(default_factory=dict)


class ApplicationContext(BaseModel):
    """Canonical context data model for Application Copilots (Blender, IDEs, Office, CAD).

    Captures active application state, process info, window handle, accessibility tree, and vision data.
    Unavailable fields default to None or empty to prevent hallucinated context.
    """

    app_name: str = Field(...)
    process_id: Optional[int] = Field(None)
    executable_path: Optional[str] = Field(None)
    window_title: Optional[str] = Field(None)
    window_handle: Optional[int] = Field(None)
    monitor_info: Optional[Dict[str, Any]] = Field(None)
    profile: Optional[ApplicationProfile] = Field(None)
    ui_accessibility_tree: Optional[List[UiaElementInfo]] = Field(None)
    ocr_vision_data: Optional[OcrExtractionResult] = Field(None)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class OfficeDocument(BaseModel):
    """Office document payload (Excel, Word, PowerPoint, PDF)."""

    doc_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    doc_type: str = Field("excel")
    file_path: str = Field(...)
    title: str = Field("Untitled")
    page_count: int = Field(1)
    word_count: int = Field(0)


class TerminalSession(BaseModel):
    """Terminal execution session payload (PowerShell, CMD, Bash, SSH)."""

    session_id: str = Field(default_factory=lambda: f"term_{uuid.uuid4().hex[:8]}")
    shell_type: str = Field("powershell")
    working_directory: str = Field("c:\\Projects\\Nova-AI")
    environment_vars: Dict[str, str] = Field(default_factory=dict)


class FileOperation(BaseModel):
    """Filesystem file action payload."""

    op_id: str = Field(default_factory=lambda: f"fop_{uuid.uuid4().hex[:8]}")
    op_type: str = Field("copy")
    source_path: str = Field(...)
    destination_path: Optional[str] = Field(None)
    bytes_transferred: int = Field(0)


class FolderOperation(BaseModel):
    """Filesystem folder action payload."""

    op_id: str = Field(default_factory=lambda: f"dir_{uuid.uuid4().hex[:8]}")
    op_type: str = Field("organize")
    folder_path: str = Field(...)
    items_count: int = Field(0)


class WorkflowExecution(BaseModel):
    """Overall automation workflow progress model."""

    execution_id: str = Field(default_factory=lambda: f"wexec_{uuid.uuid4().hex[:8]}")
    workflow_name: str = Field(...)
    status: ActionStatus = Field(ActionStatus.RUNNING)
    total_steps: int = Field(1)
    completed_steps: int = Field(0)
    duration_sec: float = Field(0.0)


class DesktopState(BaseModel):
    """Unified desktop OS state snapshot model."""

    active_app: str = Field("VS Code")
    active_window: str = Field("main.py")
    active_tab: Optional[str] = Field(None)
    active_terminal: Optional[str] = Field(None)
    monitors_count: int = Field(1)
    timestamp: float = Field(default_factory=time.time)


class DesktopMetrics(BaseModel):
    """Telemetry collector metrics model."""

    total_actions: int = Field(0)
    verified_actions: int = Field(0)
    recovered_actions: int = Field(0)
    failed_actions: int = Field(0)
    timestamp: float = Field(default_factory=time.time)


class DesktopHealth(BaseModel):
    """Health monitor status model."""

    is_healthy: bool = Field(True)
    session_active: bool = Field(True)
    active_windows_count: int = Field(1)
    active_processes_count: int = Field(1)
    timestamp: float = Field(default_factory=time.time)


class UiaElementInfo(BaseModel):
    """Windows UI Automation Accessibility Tree element model."""

    automation_id: str = Field(...)
    name: str = Field(...)
    control_type: str = Field(...)
    supported_patterns: List[str] = Field(default_factory=list)
    bounds: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "width": 100, "height": 30})
    is_enabled: bool = Field(True)
    is_visible: bool = Field(True)


class PlaywrightBrowserOptions(BaseModel):
    """Playwright browser configuration options."""

    headless: bool = Field(False)
    browser_type: str = Field("chromium")
    persistent_context: bool = Field(True)
    user_data_dir: str = Field("./data/browser_profiles/playwright")
    viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1920, "height": 1080})


class VisionLocatorResult(BaseModel):
    """Multimodal Vision (Qwen2.5-VL/Florence-2) control locator result."""

    model_name: str = Field("qwen2.5-vl")
    target_label: str = Field(...)
    bounding_box: Dict[str, int] = Field(default_factory=dict)
    confidence: float = Field(0.95)
    visual_reasoning: str = Field("")


class OcrExtractionResult(BaseModel):
    """OCR engine extraction outcome payload."""

    engine_name: str = Field("paddle_ocr")
    detected_text: str = Field(...)
    bounding_boxes: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(0.96)


class FailureAnalyticsRecord(BaseModel):
    """Failure analytics diagnostic record."""

    record_id: str = Field(default_factory=lambda: f"flog_{uuid.uuid4().hex[:8]}")
    action_id: str = Field(...)
    failure_reason: str = Field(...)
    screenshot_path: Optional[str] = Field(None)
    accessibility_tree_dump: Dict[str, Any] = Field(default_factory=dict)
    vision_output: Optional[str] = Field(None)
    ocr_text_dump: Optional[str] = Field(None)
    recovery_strategy_used: str = Field("")
    recovery_success: bool = Field(False)
    timestamp: float = Field(default_factory=time.time)


class BenchmarkMetrics(BaseModel):
    """Desktop automation performance benchmark metrics model."""

    launch_time_ms: float = Field(0.0)
    click_latency_ms: float = Field(0.0)
    vision_latency_ms: float = Field(0.0)
    ocr_latency_ms: float = Field(0.0)
    automation_success_rate: float = Field(1.0)
    recovery_success_rate: float = Field(1.0)
    cpu_utilization_percent: float = Field(0.0)
    gpu_vram_used_mb: float = Field(0.0)
    ram_used_mb: float = Field(0.0)


class GoalPlanStep(BaseModel):
    """Step node in AI goal-driven execution plan."""

    step_index: int = Field(...)
    title: str = Field(...)
    action_type: str = Field(...)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: ActionStatus = Field(ActionStatus.PENDING)


class ApplicationIdentity(BaseModel):
    """Canonical identity representation of a desktop application/process."""

    app_name: str = Field(...)
    bundle_id: Optional[str] = Field(None, description="AppX package family name, bundle ID, or process name")
    executable_name: str = Field(...)
    executable_path: Optional[str] = Field(None)
    process_id: Optional[int] = Field(None)
    window_class: Optional[str] = Field(None)
    architecture: Optional[str] = Field(None)
    is_elevated: bool = Field(False)


class ApplicationState(BaseModel):
    """Real-time observed state snapshot of an application."""

    identity: Optional[ApplicationIdentity] = Field(None)
    is_running: bool = Field(False)
    is_active: bool = Field(False)
    window_title: Optional[str] = Field(None)
    window_bounds: Optional[Dict[str, int]] = Field(None)
    active_view: Optional[str] = Field(None)
    last_observed_at: float = Field(default_factory=time.time)


