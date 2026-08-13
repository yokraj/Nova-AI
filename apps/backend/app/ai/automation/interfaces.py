"""Abstract interfaces for the Native Desktop & Browser Automation Engine."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.automation.models import (
    AutomationHealth,
    AutomationMetrics,
    AutomationRequest,
    AutomationResult,
    OCRResult,
    UIElement,
    WindowInfo,
)


class IDesktopController(ABC):
    """Abstract contract for high-level desktop OS automation."""

    @abstractmethod
    async def launch_application(self, app_name_or_path: str) -> WindowInfo:
        pass

    @abstractmethod
    async def close_application(self, app_name_or_pid: Any) -> bool:
        pass

    @abstractmethod
    async def list_windows(self) -> List[WindowInfo]:
        pass

    @abstractmethod
    async def focus_window(self, title_or_handle: Any) -> bool:
        pass


class IBrowserController(ABC):
    """Abstract contract for high-level web browser automation."""

    @abstractmethod
    async def open_browser(self, browser_type: str = "chrome") -> bool:
        pass

    @abstractmethod
    async def navigate_url(self, url: str) -> bool:
        pass

    @abstractmethod
    async def click_element(self, selector: str) -> bool:
        pass

    @abstractmethod
    async def fill_input(self, selector: str, value: str) -> bool:
        pass

    @abstractmethod
    async def take_screenshot(self, output_path: str) -> str:
        pass


class IOCREngine(ABC):
    """Abstract contract for OCR text extraction."""

    @abstractmethod
    async def extract_text_from_image(self, image_path_or_bytes: Any) -> OCRResult:
        pass

    @abstractmethod
    async def extract_text_from_pdf(self, pdf_path: str) -> OCRResult:
        pass


class IFormFiller(ABC):
    """Abstract contract for automated web form detection and filling."""

    @abstractmethod
    async def fill_form_data(self, form_selector: str, field_values: Dict[str, Any]) -> bool:
        pass


class IAutomationRuntime(ABC):
    """Abstract contract for central Automation Runtime facade."""

    @abstractmethod
    async def execute_automation(self, request: AutomationRequest) -> AutomationResult:
        pass

    @abstractmethod
    async def get_metrics(self) -> AutomationMetrics:
        pass

    @abstractmethod
    def check_health(self) -> AutomationHealth:
        pass
