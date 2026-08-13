"""Browser Controller orchestrating multi-browser engines (Chrome, Edge, Firefox), tabs, navigation, forms, JS, and file transfers."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.automation.browser_profiles import BrowserProfiles
from app.ai.automation.browser_session import BrowserSession
from app.ai.automation.cookie_manager import CookieManager
from app.ai.automation.dom_inspector import DOMInspector
from app.ai.automation.download_manager import DownloadManager
from app.ai.automation.form_filler import FormFiller
from app.ai.automation.history_manager import HistoryManager
from app.ai.automation.interfaces import IBrowserController
from app.ai.automation.javascript_executor import JavaScriptExecutor
from app.ai.automation.navigation_engine import NavigationEngine
from app.ai.automation.selector_engine import SelectorEngine
from app.ai.automation.tab_manager import TabManager
from app.ai.automation.upload_manager import UploadManager

logger = structlog.get_logger("browser_controller")


class BrowserController(IBrowserController):
    """High-level browser automation orchestrator supporting Chrome, Edge, Firefox, tabs, navigation, DOM, and forms."""

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider
        self.profiles = BrowserProfiles()
        self.session = BrowserSession()
        self.tabs = TabManager()
        self.downloads = DownloadManager()
        self.uploads = UploadManager()
        self.navigation = NavigationEngine()
        self.forms = FormFiller()
        self.dom = DOMInspector()
        self.js = JavaScriptExecutor()
        self.selectors = SelectorEngine()
        self.cookies = CookieManager()
        self.history = HistoryManager()

    async def open_browser(self, browser_type: str = "chrome") -> bool:
        """Launch target web browser engine."""
        self.session = BrowserSession(browser_type=browser_type)
        await self.session.start()

        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.open_url("about:blank")

        logger.info("Opened browser", browser_type=browser_type)
        return True

    async def close_browser(self) -> bool:
        """Close active web browser engine."""
        await self.session.close()
        logger.info("Closed browser")
        return True

    async def open_url(self, url: str) -> None:
        """Launches target URL."""
        await self.navigate_url(url)

    async def navigate_url(self, url: str) -> bool:
        """Navigate active tab to target URL."""
        target_url = await self.navigation.navigate(url)
        await self.history.add_history(target_url)

        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.navigate(url)

        logger.info("Navigated to URL", url=target_url)
        return True

    async def new_tab(self, url: str = "about:blank") -> Dict[str, str]:
        """Open new browser tab."""
        return await self.tabs.create_tab(url)

    async def close_tab(self, tab_id: str) -> bool:
        """Close specified browser tab."""
        return await self.tabs.close_tab(tab_id)

    async def switch_tab(self, tab_id: str) -> Dict[str, str]:
        """Switch active browser tab."""
        return await self.tabs.switch_tab(tab_id)

    async def click_element(self, selector: str) -> bool:
        """Click element matching selector."""
        resolved = self.selectors.resolve_selector(selector)
        logger.info("Clicked browser element", selector=resolved)

        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.click_element(selector)

        return True

    async def fill_input(self, selector: str, value: str) -> bool:
        """Fill input element matching selector."""
        resolved = self.selectors.resolve_selector(selector)
        logger.info("Filled browser input", selector=resolved, value_length=len(value))

        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.fill_input(selector, value)

        return True

    async def fill_form(self, form_selector: str, data: Dict[str, Any]) -> bool:
        """Fill and submit form."""
        await self.forms.fill_form_data(form_selector, data)
        return await self.forms.submit_form(form_selector)

    async def download_file(self, url: str, filename: str) -> str:
        """Download file from page."""
        return await self.downloads.handle_download(url, filename)

    async def upload_file(self, selector: str, file_path: str) -> bool:
        """Upload file via input element."""
        return await self.uploads.upload_file(selector, file_path)

    async def take_screenshot(self, output_path: str) -> str:
        """Capture page screenshot."""
        logger.info("Captured browser page screenshot", path=output_path)

        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.screenshot(output_path)

        return output_path

    async def screenshot(self, output_path: str) -> None:
        """Legacy helper matching existing calls."""
        await self.take_screenshot(output_path)

    async def refresh(self) -> None:
        """Reload page."""
        await self.navigation.refresh()
        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.refresh()

    async def back(self) -> None:
        """Page back."""
        await self.navigation.back()
        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.back()

    async def forward(self) -> None:
        """Page forward."""
        await self.navigation.forward()
        if self.provider and hasattr(self.provider, "browser"):
            await self.provider.browser.forward()

    async def execute_javascript(self, script: str) -> Any:
        """Execute JS in page context."""
        return await self.js.execute_js(script)
