"""Desktop Plugin providing window management, app launch, and mouse/keyboard control."""

from app.ai.plugins.models import PermissionType, RiskLevel
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult


@nova_plugin(
    name="Desktop",
    version="1.0.0",
    description="Desktop app automation and UI control plugin.",
    permissions=[PermissionType.DESKTOP, PermissionType.CLIPBOARD],
)
class DesktopPlugin(BasePlugin):
    """Reference implementation of Desktop Plugin bound to Native DesktopController."""

    @capability(
        name="launch_app",
        description="Launch a desktop application by name or path",
        voice_intents=["launch application", "open app", "start program"],
        risk_level=RiskLevel.HIGH,
    )
    async def launch_app(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.desktop_controller import DesktopController
        app_name = context.parameters.get("app_name", "notepad")
        ctrl = DesktopController()
        win = await ctrl.launch_application(app_name)
        return PluginResult.ok(data={"status": "launched", "app": app_name, "pid": win.pid})

    @capability(
        name="control_window",
        description="Minimize, maximize, or close active application window",
        voice_intents=["minimize window", "maximize window", "close window"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def control_window(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.desktop_controller import DesktopController
        from app.ai.automation.models import WindowAction
        action = context.parameters.get("action", "maximize")
        ctrl = DesktopController()
        await ctrl.control_window("active", WindowAction.MAXIMIZE)
        return PluginResult.ok(data={"status": "executed", "action": action})

    @capability(
        name="move_mouse",
        description="Move mouse pointer to coordinates",
        voice_intents=["move mouse"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def move_mouse(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.desktop_controller import DesktopController
        x = context.parameters.get("x", 100)
        y = context.parameters.get("y", 100)
        ctrl = DesktopController()
        await ctrl.mouse_click(x, y)
        return PluginResult.ok(data={"status": "moved", "coords": (x, y)})

    @capability(
        name="keyboard_input",
        description="Simulate key presses or text typing",
        voice_intents=["type text", "press key"],
        risk_level=RiskLevel.HIGH,
    )
    async def keyboard_input(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.desktop_controller import DesktopController
        text = context.parameters.get("text", "")
        ctrl = DesktopController()
        await ctrl.type_text(text)
        return PluginResult.ok(data={"status": "typed", "length": len(text)})
