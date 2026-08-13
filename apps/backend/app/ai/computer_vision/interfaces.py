"""Abstract base interfaces and contracts for Computer Vision & Adaptive GUI Intelligence components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.computer_vision.models import (
    AdaptiveLocatorResult,
    ApplicationProfile,
    BrowserScene,
    DesktopScene,
    DocumentStructure,
    GUIElement,
    IDEScene,
    ReasoningPurpose,
    RecoveryPlan,
    ScreenHistoryItem,
    VisionHealth,
    VisionMetrics,
    VisualReasoningResult,
)


class IDesktopSceneAnalyzer(ABC):
    """Desktop Scene Analyzer contract."""

    @abstractmethod
    async def analyze_desktop(self, monitor_index: int = 0) -> DesktopScene:
        """Captures desktop and identifies window hierarchy, dialogs, buttons, text fields."""
        pass


class IGUIUnderstandingEngine(ABC):
    """GUI Understanding Engine contract."""

    @abstractmethod
    async def parse_gui_elements(self, scene: DesktopScene) -> List[GUIElement]:
        """Understands GUI semantics (Save, Cancel, Search, Login) with confidence scores."""
        pass


class IVisualReasoningEngine(ABC):
    """Visual Reasoning Engine contract."""

    @abstractmethod
    async def reason_about_screen(self, scene: DesktopScene, purpose: ReasoningPurpose) -> VisualReasoningResult:
        """Reasons over screenshot to diagnose errors, identify empty fields, guide recovery."""
        pass


class IApplicationProfileEngine(ABC):
    """Application Profile Engine contract."""

    @abstractmethod
    async def get_profile(self, app_name_or_process: str) -> ApplicationProfile:
        """Retrieves reusable application profile for Chrome, VS Code, Excel, etc."""
        pass


class IAdaptiveLocator(ABC):
    """Adaptive UI Locator contract."""

    @abstractmethod
    async def locate_element(self, query: str, scene: DesktopScene, strategy_preference: str = "accessibility_api") -> AdaptiveLocatorResult:
        """Finds UI controls dynamically via accessibility APIs, DOM, OCR, layout."""
        pass


class IDocumentUnderstandingEngine(ABC):
    """OCR & Document Understanding contract."""

    @abstractmethod
    async def parse_document(self, document_path_or_bytes: Any) -> DocumentStructure:
        """Reads PDFs, images, receipts, forms, tables, and flowcharts into DocumentStructure."""
        pass


class IIDEUnderstandingEngine(ABC):
    """IDE Understanding Engine contract."""

    @abstractmethod
    async def analyze_ide_screen(self) -> IDEScene:
        """Understands active file, open tabs, terminal, debugger, errors, warnings."""
        pass


class IBrowserUnderstandingEngine(ABC):
    """Browser Page Understanding contract."""

    @abstractmethod
    async def analyze_browser_page(self, url: str = "") -> BrowserScene:
        """Understands page purpose, forms, checkout, login, tables, and active alerts."""
        pass


class IAutomationRecovery(ABC):
    """Adaptive Automation Recovery contract."""

    @abstractmethod
    async def recover_automation(self, failed_action: str, scene: DesktopScene) -> RecoveryPlan:
        """Recovers failed desktop/browser automation without user intervention."""
        pass


class IScreenMemory(ABC):
    """Screen Memory contract."""

    @abstractmethod
    async def record_screen(self, scene: DesktopScene, action: Optional[str] = None) -> None:
        """Remembers recent screens, navigation paths, and visual changes."""
        pass

    @abstractmethod
    async def get_history(self, limit: int = 10) -> List[ScreenHistoryItem]:
        """Returns visual screen navigation history."""
        pass


class IMultiMonitorManager(ABC):
    """Multi-Monitor Support contract."""

    @abstractmethod
    def list_monitors(self) -> List[Dict[str, Any]]:
        """Returns details of all connected monitors."""
        pass


class IVisionAgent(ABC):
    """Vision Agent contract."""

    @abstractmethod
    async def execute_visual_task(self, task_description: str) -> Dict[str, Any]:
        """Performs specialized visual analysis, UI guidance, or diagram interpretation."""
        pass


class IVisionManager(ABC):
    """Vision Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts vision engine."""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """Pauses vision processing."""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """Resumes vision processing."""
        pass


class IComputerVisionEngine(ABC):
    """Central Computer Vision Engine facade contract."""

    @abstractmethod
    async def analyze_screen(self, monitor_index: int = 0) -> DesktopScene:
        """Captures and analyzes active desktop scene."""
        pass

    @abstractmethod
    async def understand_application(self, app_name: str) -> ApplicationProfile:
        """Retrieves UI layout profile and workflows for an application."""
        pass

    @abstractmethod
    async def find_ui_element(self, query: str, **kwargs: Any) -> AdaptiveLocatorResult:
        """Finds UI element matching query dynamically."""
        pass

    @abstractmethod
    async def reason_about_screen(self, query: str = "") -> VisualReasoningResult:
        """Performs visual reasoning over current desktop."""
        pass

    @abstractmethod
    async def capture_desktop(self) -> DesktopScene:
        """Captures full desktop snapshot."""
        pass

    @abstractmethod
    async def capture_window(self, window_title: str) -> DesktopScene:
        """Captures specific window snapshot."""
        pass

    @abstractmethod
    async def capture_region(self, x: int, y: int, width: int, height: int) -> DesktopScene:
        """Captures bounding box screen region."""
        pass

    @abstractmethod
    async def screen_history(self) -> List[ScreenHistoryItem]:
        """Retrieves screen memory audit history."""
        pass
