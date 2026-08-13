"""Desktop Controller orchestrating OS window control, input events, screen capture, OCR, and process management."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.automation.application_launcher import ApplicationLauncher
from app.ai.automation.clipboard_manager import ClipboardManager
from app.ai.automation.image_locator import ImageLocator
from app.ai.automation.interfaces import IDesktopController
from app.ai.automation.keyboard_controller import KeyboardController
from app.ai.automation.models import ImageMatch, OCRResult, WindowAction, WindowInfo
from app.ai.automation.mouse_controller import MouseController
from app.ai.automation.ocr_engine import OCREngine
from app.ai.automation.process_manager import ProcessManager
from app.ai.automation.screen_capture import ScreenCapture
from app.ai.automation.ui_element_detector import UIElementDetector
from app.ai.automation.window_manager import WindowManager

logger = structlog.get_logger("desktop_controller")


class DesktopController(IDesktopController):
    """High-level desktop automation orchestrator unifying mouse, keyboard, windows, OCR, and applications."""

    def __init__(self) -> None:
        self.window_mgr = WindowManager()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.clipboard = ClipboardManager()
        self.launcher = ApplicationLauncher()
        self.processes = ProcessManager()
        self.capture = ScreenCapture()
        self.ocr = OCREngine()
        self.locator = ImageLocator()
        self.ui_detector = UIElementDetector()

    async def launch_application(self, app_name_or_path: str) -> WindowInfo:
        """Launch desktop software application."""
        return await self.launcher.launch(app_name_or_path)

    async def close_application(self, app_name_or_pid: Any) -> bool:
        """Close software application."""
        return await self.processes.terminate(str(app_name_or_pid))

    async def list_windows(self) -> List[WindowInfo]:
        """List active desktop windows."""
        return await self.window_mgr.list_windows()

    async def focus_window(self, title_or_handle: Any) -> bool:
        """Bring window to foreground."""
        win = await self.window_mgr.focus_window(title_or_handle)
        return win.is_active

    async def control_window(self, title_or_handle: Any, action: WindowAction, **kwargs: Any) -> WindowInfo:
        """Perform focus, move, resize, minimize, maximize, or restore action on window."""
        return await self.window_mgr.perform_action(title_or_handle, action, **kwargs)

    async def mouse_click(self, x: int, y: int, button: str = "left") -> bool:
        """Click mouse at screen coordinates."""
        await self.mouse.click(x, y, button=button)
        return True

    async def type_text(self, text: str) -> bool:
        """Type text string."""
        await self.keyboard.type_text(text)
        return True

    async def copy_paste(self, text: str) -> str:
        """Set text in clipboard and trigger paste hotkey."""
        await self.clipboard.set_text(text)
        await self.keyboard.hotkey(["ctrl", "v"])
        return text

    async def extract_ocr_text(self, target: Optional[str] = None) -> OCRResult:
        """Extract text from screen capture or image file using OCR."""
        img_path = await self.capture.capture_full_screen()
        return await self.ocr.extract_text_from_image(img_path)

    async def locate_button_image(self, template_path: str) -> ImageMatch:
        """Locate button or icon using template matching."""
        return await self.locator.locate_template(template_path)
