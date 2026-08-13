"""Unit tests for the Native Desktop & Browser Automation Engine."""

import pytest
from app.ai.automation.automation_pipeline import AutomationPipeline
from app.ai.automation.automation_runtime import AutomationRuntime
from app.ai.automation.browser_controller import BrowserController
from app.ai.automation.clipboard_manager import ClipboardManager
from app.ai.automation.configuration import AutomationConfiguration
from app.ai.automation.desktop_controller import DesktopController
from app.ai.automation.download_manager import DownloadManager
from app.ai.automation.exceptions import AutomationError, AutomationSafetyError
from app.ai.automation.form_filler import FormFiller
from app.ai.automation.keyboard_controller import KeyboardController
from app.ai.automation.models import ActionType, AutomationRequest, WindowAction
from app.ai.automation.mouse_controller import MouseController
from app.ai.automation.ocr_engine import OCREngine
from app.ai.automation.permission_manager import AutomationPermissionManager
from app.ai.automation.tab_manager import TabManager
from app.ai.automation.window_manager import WindowManager
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve


@pytest.mark.anyio
async def test_automation_configuration():
    """Verifies default automation configuration settings."""
    config = AutomationConfiguration()
    assert config.enabled is True
    assert config.default_browser == "chrome"
    assert config.screen_width == 1920
    assert config.screen_height == 1080


@pytest.mark.anyio
async def test_desktop_controller_and_windows():
    """Verifies desktop automation application launching, window listing, and focusing."""
    ctrl = DesktopController()
    win = await ctrl.launch_application("notepad.exe")
    assert win.title == "Notepad.Exe"
    assert win.is_active is True

    windows = await ctrl.list_windows()
    assert len(windows) >= 3

    focused = await ctrl.focus_window("Google Chrome")
    assert focused is True


@pytest.mark.anyio
async def test_mouse_keyboard_clipboard():
    """Verifies mouse, keyboard, and clipboard operations."""
    mouse = MouseController()
    pos = await mouse.click(100, 200)
    assert pos == (100, 200)

    kb = KeyboardController()
    typed = await kb.type_text("Hello Nova")
    assert typed == "Hello Nova"

    clip = ClipboardManager()
    await clip.set_text("Clipboard Data")
    val = await clip.get_text()
    assert val == "Clipboard Data"


@pytest.mark.anyio
async def test_ocr_and_image_match():
    """Verifies OCR text extraction and image matching."""
    ocr = OCREngine()
    res = await ocr.extract_text_from_image("sample.png")
    assert "Error:" in res.text
    assert res.confidence > 0.9

    pdf_res = await ocr.extract_text_from_pdf("doc.pdf")
    assert "doc.pdf" in pdf_res.text


@pytest.mark.anyio
async def test_browser_controller_and_tabs():
    """Verifies multi-browser navigation and tab management."""
    browser = BrowserController()
    await browser.open_browser("chrome")
    assert browser.session.is_active is True

    await browser.navigate_url("https://python.org")
    assert browser.navigation.current_url == "https://python.org"

    tab = await browser.new_tab("https://nova.ai")
    assert tab["url"] == "https://nova.ai"

    tabs = await browser.tabs.list_tabs()
    assert len(tabs) == 2


@pytest.mark.anyio
async def test_form_filler_and_downloads():
    """Verifies automatic form filling and download interception."""
    filler = FormFiller()
    fields = await filler.detect_fields("form")
    assert len(fields) >= 5

    filled = await filler.fill_form_data("form", {"username": "nova_user"})
    assert filled is True

    dm = DownloadManager()
    file_path = await dm.handle_download("https://python.org/doc.pdf", "doc.pdf")
    assert "doc.pdf" in file_path


@pytest.mark.anyio
async def test_permission_interception():
    """Verifies dangerous action interception and safety checks."""
    perm = AutomationPermissionManager(config=AutomationConfiguration(safety_dry_run=True))
    allowed = await perm.verify_permission("make_payment", {"amount": 100})
    assert allowed is True


@pytest.mark.anyio
async def test_automation_runtime_facade():
    """Verifies central AutomationRuntime execution, metrics, and health."""
    runtime = AutomationRuntime()

    req_desktop = AutomationRequest(
        action_type=ActionType.DESKTOP,
        action_name="launch",
        parameters={"app": "cmd.exe"},
    )
    res_desktop = await runtime.execute_automation(req_desktop)
    assert res_desktop.success is True

    req_browser = AutomationRequest(
        action_type=ActionType.BROWSER,
        action_name="navigate",
        parameters={"url": "https://google.com"},
    )
    res_browser = await runtime.execute_automation(req_browser)
    assert res_browser.success is True

    metrics = await runtime.get_metrics()
    assert metrics.total_automations == 2
    assert metrics.desktop_actions_count == 1
    assert metrics.browser_actions_count == 1

    health = runtime.check_health()
    assert health.status == "healthy"


@pytest.mark.anyio
async def test_gateway_automation_apis():
    """Verifies AI Gateway automation methods."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    app_res = await gateway.open_application("notepad.exe")
    assert app_res["success"] is True

    browser_res = await gateway.control_browser("navigate", url="https://python.org")
    assert browser_res["success"] is True
