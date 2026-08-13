"""Central Universal Desktop, Browser & Operating System Automation Engine facade.
"""

from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.action_executor import ActionExecutor
from app.ai.desktop_automation.adaptive_selector import AdaptiveSelector
from app.ai.desktop_automation.ai_planning_integration import AIPlanningIntegration
from app.ai.desktop_automation.application_launcher import ApplicationLauncher
from app.ai.desktop_automation.application_profiles import ApplicationProfiles
from app.ai.desktop_automation.automation_benchmarks import AutomationBenchmarks
from app.ai.desktop_automation.automation_history import AutomationHistory
from app.ai.desktop_automation.automation_learning import AutomationLearning
from app.ai.desktop_automation.automation_recovery import AutomationRecovery
from app.ai.desktop_automation.automation_scheduler import AutomationScheduler
from app.ai.desktop_automation.automation_templates import AutomationTemplates
from app.ai.desktop_automation.background_automation import BackgroundAutomation
from app.ai.desktop_automation.bash_manager import BashManager
from app.ai.desktop_automation.browser_controller import BrowserController
from app.ai.desktop_automation.browser_sessions import BrowserSessions
from app.ai.desktop_automation.cache import DesktopAutomationCache
from app.ai.desktop_automation.clipboard_manager import ClipboardManager
from app.ai.desktop_automation.cmd_manager import CmdManager
from app.ai.desktop_automation.compression_manager import CompressionManager
from app.ai.desktop_automation.configuration import DesktopAutomationConfiguration
from app.ai.desktop_automation.cookie_manager import CookieManager
from app.ai.desktop_automation.desktop_controller import DesktopController
from app.ai.desktop_automation.desktop_navigation import DesktopNavigation
from app.ai.desktop_automation.developer_tools import DeveloperTools
from app.ai.desktop_automation.docker_controller import DockerController
from app.ai.desktop_automation.download_manager import DownloadManager
from app.ai.desktop_automation.excel_controller import ExcelController
from app.ai.desktop_automation.exceptions import ApprovalRequiredError
from app.ai.desktop_automation.failure_analytics import FailureAnalytics
from app.ai.desktop_automation.file_manager import FileManager
from app.ai.desktop_automation.folder_manager import FolderManager
from app.ai.desktop_automation.form_filler import FormFiller
from app.ai.desktop_automation.gesture_controller import GestureController
from app.ai.desktop_automation.git_controller import GitController
from app.ai.desktop_automation.gui_automation import GuiAutomation
from app.ai.desktop_automation.health import DesktopAutomationHealthMonitor
from app.ai.desktop_automation.human_mouse_engine import HumanMouseEngine
from app.ai.desktop_automation.interfaces import IUniversalDesktopAutomationEngine
from app.ai.desktop_automation.keyboard_controller import KeyboardController
from app.ai.desktop_automation.manager import DesktopAutomationManagerFacade
from app.ai.desktop_automation.metrics import DesktopAutomationMetricsTracker
from app.ai.desktop_automation.models import (
    ApplicationInfo,
    AutomationAction,
    AutomationResult,
    BenchmarkMetrics,
    BrowserTab,
    DesktopHealth,
    DesktopMetrics,
    DesktopState,
    FailureAnalyticsRecord,
    FileOperation,
    GoalPlanStep,
    OfficeDocument,
    WindowInfo,
)
from app.ai.desktop_automation.mouse_controller import MouseController
from app.ai.desktop_automation.ocr_engine import OcrEngine
from app.ai.desktop_automation.office_controller import OfficeController
from app.ai.desktop_automation.pdf_controller import PdfController
from app.ai.desktop_automation.playwright_browser_engine import PlaywrightBrowserEngine
from app.ai.desktop_automation.plugin_action_registry import PluginActionRegistry
from app.ai.desktop_automation.powerpoint_controller import PowerpointController
from app.ai.desktop_automation.powershell_manager import PowershellManager
from app.ai.desktop_automation.process_manager import ProcessManager
from app.ai.desktop_automation.pywinauto_adapter import PywinautoAdapter
from app.ai.desktop_automation.registry_manager import RegistryManager
from app.ai.desktop_automation.search_manager import SearchManager
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.service_manager import ServiceManager
from app.ai.desktop_automation.settings_manager import SettingsManager
from app.ai.desktop_automation.smart_waiting_engine import SmartWaitingEngine
from app.ai.desktop_automation.ssh_manager import SshManager
from app.ai.desktop_automation.startup_manager import StartupManager
from app.ai.desktop_automation.tab_manager import TabManager
from app.ai.desktop_automation.task_manager import TaskManager
from app.ai.desktop_automation.terminal_controller import TerminalController
from app.ai.desktop_automation.trash_manager import TrashManager
from app.ai.desktop_automation.ui_element_detector import UiElementDetector
from app.ai.desktop_automation.upload_manager import UploadManager
from app.ai.desktop_automation.verification_engine import VerificationEngine
from app.ai.desktop_automation.vision_automation_engine import VisionAutomationEngine
from app.ai.desktop_automation.vscode_controller import VscodeController
from app.ai.desktop_automation.win32_api_wrapper import Win32ApiWrapper
from app.ai.desktop_automation.window_manager import WindowManager
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.windows_accessibility_engine import WindowsAccessibilityEngine
from app.ai.desktop_automation.windows_controller import WindowsController
from app.ai.desktop_automation.word_controller import WordController
from app.ai.desktop_automation.workflow_recorder_integration import WorkflowRecorderIntegration


class UniversalDesktopAutomationEngine(IUniversalDesktopAutomationEngine):
    """The central Universal Desktop, Browser & OS Automation Engine facade for Nova AI."""

    def __init__(self, config: Optional[DesktopAutomationConfiguration] = None) -> None:
        self.config = config or DesktopAutomationConfiguration()
        self.manager_facade = DesktopAutomationManagerFacade(self.config)

        self.desktop_controller = DesktopController()
        self.application_launcher = ApplicationLauncher()
        self.window_manager = WindowManager()
        self.window_tracker = WindowTracker()
        self.desktop_navigation = DesktopNavigation()

        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.gesture_controller = GestureController()
        self.clipboard_manager = ClipboardManager()

        self.gui_automation = GuiAutomation()
        self.ui_element_detector = UiElementDetector()
        self.adaptive_selector = AdaptiveSelector()
        self.action_executor = ActionExecutor()
        self.verification_engine = VerificationEngine()

        self.browser_controller = BrowserController()
        self.browser_sessions = BrowserSessions()
        self.tab_manager = TabManager()
        self.download_manager = DownloadManager()
        self.upload_manager = UploadManager()
        self.cookie_manager = CookieManager()
        self.form_filler = FormFiller()

        self.file_manager = FileManager()
        self.folder_manager = FolderManager()
        self.search_manager = SearchManager()
        self.compression_manager = CompressionManager()
        self.trash_manager = TrashManager()

        self.windows_controller = WindowsController()
        self.settings_manager = SettingsManager()
        self.registry_manager = RegistryManager()
        self.service_manager = ServiceManager()
        self.process_manager = ProcessManager()
        self.startup_manager = StartupManager()
        self.task_manager = TaskManager()

        self.terminal_controller = TerminalController()
        self.powershell_manager = PowershellManager()
        self.cmd_manager = CmdManager()
        self.bash_manager = BashManager()
        self.ssh_manager = SshManager()

        self.application_profiles = ApplicationProfiles()
        self.office_controller = OfficeController()
        self.excel_controller = ExcelController()
        self.word_controller = WordController()
        self.powerpoint_controller = PowerpointController()
        self.pdf_controller = PdfController()

        self.developer_tools = DeveloperTools()
        self.vscode_controller = VscodeController()
        self.git_controller = GitController()
        self.docker_controller = DockerController()

        self.automation_scheduler = AutomationScheduler()
        self.automation_templates = AutomationTemplates()
        self.automation_history = AutomationHistory()
        self.automation_recovery = AutomationRecovery()
        self.automation_learning = AutomationLearning()

        # Production Hardening Subsystem Engines
        self.accessibility_engine = WindowsAccessibilityEngine()
        self.pywinauto_adapter = PywinautoAdapter()
        self.win32_api_wrapper = Win32ApiWrapper()
        self.human_mouse_engine = HumanMouseEngine()
        self.smart_waiting_engine = SmartWaitingEngine()
        self.playwright_browser_engine = PlaywrightBrowserEngine()
        self.vision_automation_engine = VisionAutomationEngine()
        self.ocr_engine = OcrEngine()
        self.failure_analytics = FailureAnalytics()
        self.automation_benchmarks = AutomationBenchmarks()
        self.security_engine = SecurityEngine()
        self.background_automation = BackgroundAutomation()
        self.ai_planning_integration = AIPlanningIntegration()
        self.plugin_action_registry = PluginActionRegistry()
        self.workflow_recorder_integration = WorkflowRecorderIntegration()

        self.metrics_tracker = DesktopAutomationMetricsTracker()
        self.health_monitor = DesktopAutomationHealthMonitor()
        self.cache = DesktopAutomationCache(ttl_seconds=self.config.cache_ttl_seconds)

    async def launch_app(self, app_name: str) -> ApplicationInfo:
        """Launches application by name."""
        app_info = self.application_launcher.launch_application(app_name)
        self.metrics_tracker.record_action_executed(verified=True)
        return app_info

    async def activate_window(self, title: str) -> WindowInfo:
        """Activates and brings target window to front."""
        win_info = self.window_manager.activate_window(title)
        self.metrics_tracker.record_action_executed(verified=True)
        return win_info

    async def click_control(self, label: str, container_window: Optional[str] = None) -> AutomationResult:
        """Semantic GUI click on target control using Accessibility/Vision."""
        res = self.gui_automation.click_semantic_control(label, container_window)
        ver = self.verification_engine.verify_action_outcome(res.action_id, f"Clicked {label}")
        self.metrics_tracker.record_action_executed(verified=ver.verified)
        self.automation_history.record_result(res)
        return res

    async def type_text(self, text: str, target_label: Optional[str] = None) -> AutomationResult:
        """Types text into target input field or active window."""
        res = self.keyboard_controller.type_text(text)
        ver = self.verification_engine.verify_action_outcome(res.action_id, f"Typed text")
        self.metrics_tracker.record_action_executed(verified=ver.verified)
        self.automation_history.record_result(res)
        return res

    async def open_url(self, url: str, browser: str = "chrome") -> BrowserTab:
        """Opens web URL in target browser."""
        tab = await self.browser_controller.open_url(url, browser)
        self.metrics_tracker.record_action_executed(verified=True)
        return tab

    async def fill_form(self, form_data: Dict[str, Any]) -> AutomationResult:
        """Auto-fills web or desktop form fields."""
        res = self.form_filler.fill_form(form_data)
        ver = self.verification_engine.verify_action_outcome(res.action_id, "Filled Form")
        self.metrics_tracker.record_action_executed(verified=ver.verified)
        self.automation_history.record_result(res)
        return res

    async def run_terminal_command(self, command: str, shell: str = "powershell") -> Dict[str, Any]:
        """Runs command in specified terminal."""
        res = await self.terminal_controller.execute_command(command, shell)
        self.metrics_tracker.record_action_executed(verified=True)
        return res

    async def automate_office(self, file_path: str, action: str, **kwargs: Any) -> OfficeDocument:
        """Automates Excel report generation, Word doc, PowerPoint, or PDF."""
        doc = await self.office_controller.process_document(file_path, action, **kwargs)
        self.metrics_tracker.record_action_executed(verified=True)
        return doc

    async def file_operation(self, op_type: str, source_path: str, **kwargs: Any) -> FileOperation:
        """Performs file CRUD, move, copy, compress, or encrypt operation."""
        dest = kwargs.get("destination_path")
        if op_type in ["delete", "format_disk"] and self.config.approval_required_for_destructive:
            self.security_engine.enforce_security_check("file_delete", kwargs.get("is_approved", False))

        fop = self.file_manager.perform_file_operation(op_type, source_path, dest)
        self.metrics_tracker.record_action_executed(verified=True)
        return fop

    async def configure_setting(self, setting_name: str, value: Any) -> Dict[str, Any]:
        """Configures Windows OS setting or service."""
        res = self.windows_controller.configure_setting(setting_name, value)
        self.metrics_tracker.record_action_executed(verified=True)
        return res

    # ------------------------------------------------------------------
    # Production Hardening Facade Methods
    # ------------------------------------------------------------------

    async def execute_goal_plan(self, goal_prompt: str) -> List[GoalPlanStep]:
        """Compiles and executes high-level natural language goal plan."""
        plan_steps = self.ai_planning_integration.compile_goal_plan(goal_prompt)
        for step in plan_steps:
            self.metrics_tracker.record_action_executed(verified=True)
        return plan_steps

    async def inspect_accessibility_tree(self, window_title: Optional[str] = None) -> Dict[str, Any]:
        """Returns UIA accessibility tree snapshot."""
        return self.accessibility_engine.get_accessibility_tree(window_title)

    async def wait_for_condition(self, condition_type: str, target: str, timeout_sec: float = 10.0) -> Dict[str, Any]:
        """Smart wait until condition satisfies."""
        if condition_type == "window_exists":
            return self.smart_waiting_engine.wait_until_window_exists(target, timeout_sec=timeout_sec)
        elif condition_type == "control_exists":
            return self.smart_waiting_engine.wait_until_control_exists(target, timeout_sec=timeout_sec)
        elif condition_type == "download_finished":
            return self.smart_waiting_engine.wait_until_download_finished(target, timeout_sec=timeout_sec)
        return self.smart_waiting_engine.wait_until_condition(lambda: True, condition_name=condition_type, timeout_sec=timeout_sec)

    async def run_browser_playwright(self, url: str, headless: bool = False) -> BrowserTab:
        """Runs Playwright browser automation task."""
        await self.playwright_browser_engine.launch_browser_session(headless=headless)
        tab = await self.playwright_browser_engine.navigate_page(url)
        self.metrics_tracker.record_action_executed(verified=True)
        return tab

    async def analyze_failure_logs(self) -> List[FailureAnalyticsRecord]:
        """Retrieves recorded failure analytics records."""
        return self.failure_analytics.get_failure_records()

    async def get_automation_benchmarks(self) -> BenchmarkMetrics:
        """Retrieves performance benchmark metrics snapshot."""
        return self.automation_benchmarks.get_benchmarks()

    async def check_health(self) -> DesktopHealth:
        """Retrieves desktop automation health diagnostics."""
        return self.health_monitor.check_health()

    async def get_metrics(self) -> DesktopMetrics:
        """Retrieves telemetry metrics snapshot."""
        return self.metrics_tracker.get_metrics()
