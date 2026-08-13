"""Browser Plugin providing local web navigation, element interaction, and screenshots."""

from typing import Any, Dict
from app.ai.plugins.models import CapabilityType, PermissionType, RiskLevel
from app.ai.plugins.sdk.decorators import capability, nova_plugin
from app.ai.plugins.sdk.plugin import BasePlugin
from app.ai.plugins.sdk.responses import PluginResult
from app.ai.plugins.sdk.context import PluginContext


@nova_plugin(
    name="Browser",
    version="1.0.0",
    description="Local web browser automation and navigation plugin.",
    permissions=[PermissionType.BROWSER, PermissionType.NETWORK],
)
class BrowserPlugin(BasePlugin):
    """Reference implementation of Browser Plugin bound to Native BrowserController."""

    @capability(
        name="open_url",
        description="Navigate to a specified web URL",
        voice_intents=["open website", "navigate to url", "open chrome"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def open_url(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.browser_controller import BrowserController
        url = context.parameters.get("url", "https://nova.ai")
        ctrl = BrowserController()
        await ctrl.navigate_url(url)
        return PluginResult.ok(data={"status": "opened", "url": url})

    @capability(
        name="click_element",
        description="Click an element on the active page",
        voice_intents=["click element", "click button"],
        risk_level=RiskLevel.LOW,
    )
    async def click_element(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.browser_controller import BrowserController
        selector = context.parameters.get("selector", "button")
        ctrl = BrowserController()
        await ctrl.click_element(selector)
        return PluginResult.ok(data={"status": "clicked", "selector": selector})

    @capability(
        name="fill_form",
        description="Fill out input fields in a web form",
        voice_intents=["fill form", "enter text into form"],
        risk_level=RiskLevel.MEDIUM,
    )
    async def fill_form(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.browser_controller import BrowserController
        fields = context.parameters.get("fields", {})
        ctrl = BrowserController()
        await ctrl.fill_form("form", fields)
        return PluginResult.ok(data={"status": "filled", "field_count": len(fields)})

    @capability(
        name="take_screenshot",
        description="Capture screenshot of active browser window",
        voice_intents=["take screenshot", "capture screen"],
        risk_level=RiskLevel.LOW,
    )
    async def take_screenshot(self, context: PluginContext) -> PluginResult:
        from app.ai.automation.browser_controller import BrowserController
        filename = context.parameters.get("filename", "screenshot.png")
        ctrl = BrowserController()
        out_path = await ctrl.take_screenshot(filename)
        return PluginResult.ok(data={"status": "captured", "file": out_path})
