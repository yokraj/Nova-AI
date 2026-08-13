"""Mock Desktop Automation Provider returning deterministic responses for offline unit tests and CI.
"""

from typing import Any, Dict
from app.ai.desktop_automation.models import ApplicationInfo, AutomationResult, BrowserTab, WindowInfo


class MockDesktopAutomationProvider:
    """Mock Desktop Automation Provider returning deterministic responses for unit tests."""

    async def mock_launch_app(self, app_name: str) -> ApplicationInfo:
        return ApplicationInfo(name=app_name, process_id=9999, is_running=True)

    async def mock_activate_window(self, title: str) -> WindowInfo:
        return WindowInfo(title=title, class_name="MockWindow", is_active=True)

    async def mock_click_control(self, label: str) -> AutomationResult:
        return AutomationResult(action_id="act_mock_click", success=True, output={"clicked": label})

    async def mock_open_url(self, url: str) -> BrowserTab:
        return BrowserTab(title="Mock Tab", url=url, is_active=True)
