"""Abstract base contracts for Universal Desktop, Browser & OS Automation Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.models import (
    ApplicationContext,
    ApplicationIdentity,
    ApplicationInfo,
    ApplicationState,
    AutomationAction,
    AutomationResult,
    BrowserSession,
    BrowserTab,
    DesktopHealth,
    DesktopMetrics,
    DesktopSession,
    DesktopState,
    FileOperation,
    OfficeDocument,
    TerminalSession,
    VerificationResult,
    WindowInfo,
)


class IDesktopController(ABC):
    """Desktop Controller contract for managing desktop state, resolution, monitors, and switching."""

    @abstractmethod
    def get_desktop_state(self) -> DesktopState:
        """Returns current unified desktop OS state snapshot."""
        pass


class IWindowManager(ABC):
    """Window Manager contract for finding, activating, resizing, and snapping windows."""

    @abstractmethod
    def find_window(self, title: str) -> Optional[WindowInfo]:
        """Finds window by title substring."""
        pass


class IBrowserController(ABC):
    """Browser Controller contract for automating web browsers."""

    @abstractmethod
    async def open_url(self, url: str, browser: str = "chrome") -> BrowserTab:
        """Opens URL in specified browser."""
        pass


class IWindowsController(ABC):
    """Windows OS Controller contract for controlling Windows settings, processes, and services."""

    @abstractmethod
    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Returns Windows system diagnostic telemetry."""
        pass


class IOfficeController(ABC):
    """Office Automation Controller contract for Word, Excel, PowerPoint, and PDF files."""

    @abstractmethod
    async def process_document(self, file_path: str, action: str, **kwargs: Any) -> OfficeDocument:
        """Processes Office or PDF document."""
        pass


class ITerminalController(ABC):
    """Terminal Controller contract for PowerShell, CMD, Bash, and SSH execution."""

    @abstractmethod
    async def execute_command(self, command: str, shell: str = "powershell") -> Dict[str, Any]:
        """Executes command in specified terminal shell."""
        pass


class IDesktopAutomationManagerFacade(ABC):
    """Subsystem Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts desktop automation manager."""
        pass


class IUniversalDesktopAutomationEngine(ABC):
    """Central Universal Desktop Automation Engine facade contract."""

    @abstractmethod
    async def launch_app(self, app_name: str) -> ApplicationInfo:
        """Launches application by name."""
        pass

    @abstractmethod
    async def activate_window(self, title: str) -> WindowInfo:
        """Activates and brings target window to front."""
        pass

    @abstractmethod
    async def click_control(self, label: str, container_window: Optional[str] = None) -> AutomationResult:
        """Semantic GUI click on target control using Accessibility/Vision."""
        pass

    @abstractmethod
    async def type_text(self, text: str, target_label: Optional[str] = None) -> AutomationResult:
        """Types text into target input field or active window."""
        pass

    @abstractmethod
    async def open_url(self, url: str, browser: str = "chrome") -> BrowserTab:
        """Opens web URL in target browser."""
        pass

    @abstractmethod
    async def fill_form(self, form_data: Dict[str, Any]) -> AutomationResult:
        """Auto-fills web or desktop form fields."""
        pass

    @abstractmethod
    async def run_terminal_command(self, command: str, shell: str = "powershell") -> Dict[str, Any]:
        """Runs command in specified terminal."""
        pass

    @abstractmethod
    async def automate_office(self, file_path: str, action: str, **kwargs: Any) -> OfficeDocument:
        """Automates Excel report generation, Word doc, PowerPoint, or PDF."""
        pass

    @abstractmethod
    async def file_operation(self, op_type: str, source_path: str, **kwargs: Any) -> FileOperation:
        """Performs file CRUD, move, copy, compress, or encrypt operation."""
        pass

    @abstractmethod
    async def configure_setting(self, setting_name: str, value: Any) -> Dict[str, Any]:
        """Configures Windows OS setting or service."""
        pass

    @abstractmethod
    async def execute_goal_plan(self, goal_prompt: str) -> List[Any]:
        """Compiles and executes high-level natural language goal plan."""
        pass

    @abstractmethod
    async def inspect_accessibility_tree(self, window_title: Optional[str] = None) -> Dict[str, Any]:
        """Returns UIA accessibility tree snapshot."""
        pass

    @abstractmethod
    async def wait_for_condition(self, condition_type: str, target: str, timeout_sec: float = 10.0) -> Dict[str, Any]:
        """Smart wait until condition satisfies."""
        pass

    @abstractmethod
    async def run_browser_playwright(self, url: str, headless: bool = False) -> Any:
        """Runs Playwright browser automation task."""
        pass

    @abstractmethod
    async def analyze_failure_logs(self) -> List[Any]:
        """Retrieves recorded failure analytics records."""
        pass

    @abstractmethod
    async def get_automation_benchmarks(self) -> Any:
        """Retrieves performance benchmark metrics snapshot."""
        pass


class IApplicationAdapter(ABC):
    """Universal base contract for Application Copilot adapters (e.g. Blender, IDEs, Office, Browsers).

    Provides standard lifecycle and inspection contracts:
    - identity: ApplicationIdentity
    - capabilities: List[str]
    - current_state / observe: ApplicationState
    - action_schema / can_handle_action
    - execute / verify
    All action execution MUST route through security permission guards.
    """

    @abstractmethod
    def get_identity(self) -> Optional[ApplicationIdentity]:
        """Return application identity specification."""
        pass

    @abstractmethod
    async def detect(self) -> bool:
        """Detect if target application/process is currently active or available."""
        pass

    @abstractmethod
    async def get_context(self) -> ApplicationContext:
        """Retrieve real-time application context (process, window, accessibility tree, vision data)."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return supported copilot capabilities for this application."""
        pass

    @abstractmethod
    def get_action_schema(self, action_type: str) -> Dict[str, Any]:
        """Return validation schema/specification for target action_type."""
        pass

    @abstractmethod
    def can_handle_action(self, action: AutomationAction) -> bool:
        """Return True if this adapter supports and can execute the given action."""
        pass

    @abstractmethod
    async def observe(self) -> ApplicationState:
        """Observe real-time state snapshot of the application."""
        pass

    @abstractmethod
    async def execute(self, action: AutomationAction) -> AutomationResult:
        """Execute an action through security permission guards."""
        pass

    @abstractmethod
    async def verify(self, action: AutomationAction, result: AutomationResult) -> VerificationResult:
        """Perform post-execution empirical state verification."""
        pass



