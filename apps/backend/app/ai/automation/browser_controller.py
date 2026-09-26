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

from app.ai.automation.providers.chrome_cdp_provider import ChromeCDPBrowserProvider

logger = structlog.get_logger("browser_controller")


class BrowserController(IBrowserController):
    """High-level browser automation orchestrator supporting Chrome CDP, tabs, navigation, DOM, and forms."""

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider or ChromeCDPBrowserProvider()
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
        if hasattr(self.provider, "open_url"):
            await self.provider.open_url("about:blank")
        logger.info("Opened browser", browser_type=browser_type)
        return True

    async def close_browser(self) -> bool:
        """Close active web browser engine."""
        await self.session.close()
        if hasattr(self.provider, "close"):
            await self.provider.close()
        logger.info("Closed browser")
        return True

    async def open_url(self, url: str) -> None:
        """Launches target URL."""
        await self.navigate_url(url)

    async def navigate_url(self, url: str) -> bool:
        """Navigate active tab to target URL."""
        target_url = await self.navigation.navigate(url)
        await self.history.add_history(target_url)

        if hasattr(self.provider, "navigate"):
            await self.provider.navigate(url)

        logger.info("Navigated to URL", url=target_url)
        return True

    async def observe_page(self) -> Dict[str, Any]:
        """Observes current page state, returning URL, title, body snippet, interactive elements, forms, tabs, and viewport."""
        if hasattr(self.provider, "get_page_info"):
            return await self.provider.get_page_info()
        return {"url": "about:blank", "title": "", "bodyText": "", "interactive": [], "tabs": [], "forms": []}

    async def ground_element(self, target_query: str) -> Dict[str, Any]:
        """Adaptive multi-modal element grounding returning candidate selector, confidence, and source."""
        if hasattr(self.provider, "ground_element"):
            return await self.provider.ground_element(target_query)
        return {"selector": target_query, "confidence": 0.5, "source": "fallback", "requires_human": False}

    async def click_element(self, selector: str) -> bool:
        """Click element matching selector or text."""
        resolved = self.selectors.resolve_selector(selector)
        logger.info("Clicked browser element", selector=resolved)

        if hasattr(self.provider, "click_element"):
            return await self.provider.click_element(selector)
        return True

    async def click_element_advanced(self, selector: str, click_type: str = "single") -> bool:
        """Single, double, or right-click interaction."""
        if hasattr(self.provider, "click_element_advanced"):
            return await self.provider.click_element_advanced(selector, click_type)
        return await self.click_element(selector)

    async def fill_input(self, selector: str, value: str) -> bool:
        """Fill input element matching selector with value."""
        resolved = self.selectors.resolve_selector(selector)
        logger.info("Filled browser input", selector=resolved, value_length=len(value))

        if hasattr(self.provider, "fill_input"):
            return await self.provider.fill_input(selector, value)
        return True

    async def clear_input(self, selector: str) -> bool:
        """Clears text inside target input element."""
        if hasattr(self.provider, "clear_input"):
            return await self.provider.clear_input(selector)
        return True

    async def press_key(self, key_name: str) -> bool:
        """Dispatches key press event."""
        if hasattr(self.provider, "press_key"):
            return await self.provider.press_key(key_name)
        return True

    async def select_option(self, selector: str, option_val: str) -> bool:
        """Selects dropdown option."""
        if hasattr(self.provider, "select_option"):
            return await self.provider.select_option(selector, option_val)
        return True

    async def set_checkbox(self, selector: str, checked: bool = True) -> bool:
        """Sets checkbox checked state."""
        if hasattr(self.provider, "set_checkbox"):
            return await self.provider.set_checkbox(selector, checked)
        return True

    async def scroll_page(self, delta_x: int = 0, delta_y: int = 500) -> bool:
        """Scrolls page viewport."""
        if hasattr(self.provider, "scroll_page"):
            return await self.provider.scroll_page(delta_x, delta_y)
        return True

    async def hover_element(self, selector: str) -> bool:
        """Hovers over target element."""
        if hasattr(self.provider, "hover_element"):
            return await self.provider.hover_element(selector)
        return True

    async def wait_for_idle(self, timeout_ms: int = 5000) -> bool:
        """Dynamic wait for network and DOM idle."""
        if hasattr(self.provider, "wait_for_idle"):
            return await self.provider.wait_for_idle(timeout_ms)
        return True

    async def list_tabs(self) -> List[Dict[str, Any]]:
        """Lists active browser tabs."""
        if hasattr(self.provider, "list_tabs"):
            return await self.provider.list_tabs()
        return []

    async def switch_tab(self, tab_id: str) -> bool:
        """Switches active focus to target tab."""
        if hasattr(self.provider, "switch_tab"):
            return await self.provider.switch_tab(tab_id)
        return True

    async def new_tab(self, url: str = "about:blank") -> Dict[str, Any]:
        """Creates a new browser tab."""
        if hasattr(self.provider, "new_tab"):
            return await self.provider.new_tab(url)
        return {}

    async def close_tab(self, tab_id: str) -> bool:
        """Closes target tab."""
        if hasattr(self.provider, "close_tab"):
            return await self.provider.close_tab(tab_id)
        return True

    async def extract_structured_info(self, goal_query: str) -> Dict[str, Any]:
        """Goal-oriented web information extraction."""
        if hasattr(self.provider, "extract_structured_info"):
            return await self.provider.extract_structured_info(goal_query)
        obs = await self.observe_page()
        return {"source_url": obs.get("url"), "page_title": obs.get("title"), "extracted_facts": [obs.get("bodyText", "")[:200]]}

    async def submit_form(self, form_selector: Optional[str] = None) -> bool:
        """Submits target form or active form."""
        if hasattr(self.provider, "submit_form"):
            return await self.provider.submit_form(form_selector)
        return await self.forms.submit_form(form_selector or "")

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

        if hasattr(self.provider, "screenshot"):
            return await self.provider.screenshot(output_path)

        return output_path

    async def screenshot(self, output_path: str) -> None:
        """Legacy helper matching existing calls."""
        await self.take_screenshot(output_path)

    async def refresh(self) -> None:
        """Reload page."""
        await self.navigation.refresh()
        if hasattr(self.provider, "refresh"):
            await self.provider.refresh()

    async def back(self) -> None:
        """Page back."""
        await self.navigation.back()
        if hasattr(self.provider, "back"):
            await self.provider.back()

    async def forward(self) -> None:
        """Page forward."""
        await self.navigation.forward()
        if hasattr(self.provider, "forward"):
            await self.provider.forward()

    async def execute_javascript(self, script: str) -> Any:
        """Execute JS in page context."""
        if hasattr(self.provider, "_evaluate_js"):
            return await self.provider._evaluate_js(script)
        return await self.js.execute_js(script)

