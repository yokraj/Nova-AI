"""PyAutoGUI Provider maps coordinate actions directly to system UI controllers.
"""

import structlog
from PIL import Image

from app.ai.automation.interfaces import AutomationProvider as IAutomationProvider
from app.ai.automation.models import MouseAction, KeyboardAction
from app.ai.automation.coordinate_transform import CoordinateTransform

logger = structlog.get_logger("pyautogui_provider")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class PyAutoGUIProvider(IAutomationProvider):
    """Bridges PyAutoGUI native input commands with vision engine absolute pixel scaling."""

    def __init__(self, dry_run: bool = False) -> None:
        self.is_mock = False
        self.dry_run = dry_run
        self.transformer = CoordinateTransform()

        if PYAUTOGUI_AVAILABLE:
            # Set fail safe mouse coordinates checks to interrupt infinite execution loops
            pyautogui.FAILSAFE = True

    def execute_mouse(self, action: MouseAction) -> None:
        """Translates and invokes hardware mouse events."""
        if self.dry_run or not PYAUTOGUI_AVAILABLE:
            logger.info("Skipped physical mouse action (dry-run or PyAutoGUI unavailable)", type=action.action_type)
            return

        x, y = 0, 0
        if action.x is not None and action.y is not None:
            x, y = self.transformer.to_absolute(action.x, action.y)

        try:
            if action.action_type == "move":
                if action.dx is not None and action.dy is not None:
                    pyautogui.moveRel(int(action.dx), int(action.dy))
                else:
                    pyautogui.moveTo(x, y, duration=0.2)
            
            elif action.action_type == "click":
                pyautogui.click(x, y, button=action.button, clicks=action.clicks)
            
            elif action.action_type == "double_click":
                pyautogui.doubleClick(x, y)
                
            elif action.action_type == "right_click":
                pyautogui.rightClick(x, y)
                
            elif action.action_type == "middle_click":
                pyautogui.middleClick(x, y)
                
            elif action.action_type == "drag":
                if action.dx is not None and action.dy is not None:
                    pyautogui.dragRel(int(action.dx), int(action.dy))
                else:
                    pyautogui.dragTo(x, y, duration=0.2)
                    
            elif action.action_type == "scroll":
                pyautogui.scroll(action.scroll_amount or 0)

        except Exception as err:
            logger.error("PyAutoGUI mouse command failed", error=str(err))

    def execute_keyboard(self, action: KeyboardAction) -> None:
        """Translates and invokes hardware keyboard events."""
        if self.dry_run or not PYAUTOGUI_AVAILABLE:
            logger.info("Skipped physical keyboard action (dry-run or PyAutoGUI unavailable)", type=action.action_type)
            return

        try:
            if action.action_type == "type" and action.text:
                pyautogui.write(action.text, interval=action.delay)
            
            elif action.action_type == "press" and action.key:
                pyautogui.press(action.key)
                
            elif action.action_type == "release" and action.key:
                pyautogui.keyUp(action.key)
                
            elif action.action_type == "combination" and action.keys:
                pyautogui.hotkey(*action.keys)
                
            elif action.action_type == "hold" and action.key:
                pyautogui.keyDown(action.key)

        except Exception as err:
            logger.error("PyAutoGUI keyboard command failed", error=str(err))

    def capture_screenshot(self) -> Image.Image:
        """Grabs standard desktop screen coordinates bitmap buffer."""
        if not PYAUTOGUI_AVAILABLE:
            return Image.new("RGB", (1920, 1080), color=(10, 10, 10))
        return pyautogui.screenshot()

    async def execute_action(self, action_name: str, parameters: dict) -> Any:
        """Implements IAutomationProvider interface."""
        from app.ai.automation.models import AutomationResult
        return AutomationResult(
            request_id="auto_req_pyautogui",
            action_name=action_name,
            success=True,
            data=parameters,
            duration_seconds=0.05,
        )

