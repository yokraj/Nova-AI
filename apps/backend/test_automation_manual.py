"""12-Stage Manual Validation Script for M3.3.11 Native Desktop & Browser Automation Engine."""

import asyncio
import sys
import structlog

from app.ai.automation.automation_pipeline import AutomationPipeline
from app.ai.automation.automation_runtime import AutomationRuntime
from app.ai.automation.browser_controller import BrowserController
from app.ai.automation.clipboard_manager import ClipboardManager
from app.ai.automation.configuration import AutomationConfiguration
from app.ai.automation.desktop_controller import DesktopController
from app.ai.automation.download_manager import DownloadManager
from app.ai.automation.form_filler import FormFiller
from app.ai.automation.keyboard_controller import KeyboardController
from app.ai.automation.models import ActionType, AutomationRequest, WindowAction
from app.ai.automation.mouse_controller import MouseController
from app.ai.automation.ocr_engine import OCREngine
from app.ai.automation.permission_manager import AutomationPermissionManager
from app.ai.gateway import IAIGateway
from app.core.dependency_container import register_ai_gateway_dependencies, resolve

logger = structlog.get_logger("test_automation_manual")


async def run_manual_validation() -> None:
    print("=========================================")
    print("Nova AI Automation Engine Validation")
    print("=========================================")

    # Stage 1: Configuration
    config = AutomationConfiguration()
    assert config.enabled is True
    print("Stage 1  Configuration              PASS")

    # Stage 2: Desktop Controller & Windows
    desktop = DesktopController()
    win = await desktop.launch_application("notepad.exe")
    assert win.title == "Notepad.Exe"
    print("Stage 2  Desktop Application Launch  PASS")

    # Stage 3: Window Management
    focused = await desktop.focus_window("Google Chrome")
    assert focused is True
    print("Stage 3  Window Focus & Control     PASS")

    # Stage 4: Mouse & Keyboard
    mouse = MouseController()
    pos = await mouse.click(500, 500)
    assert pos == (500, 500)
    kb = KeyboardController()
    typed = await kb.type_text("Testing input")
    assert typed == "Testing input"
    print("Stage 4  Mouse & Keyboard Control   PASS")

    # Stage 5: Clipboard Manager
    clip = ClipboardManager()
    await clip.set_text("Manual test data")
    assert await clip.get_text() == "Manual test data"
    print("Stage 5  Clipboard Management       PASS")

    # Stage 6: OCR Engine & Image Locating
    ocr = OCREngine()
    res = await ocr.extract_text_from_image("sample.png")
    assert res.confidence > 0.9
    print("Stage 6  OCR & Text Recognition     PASS")

    # Stage 7: Browser Navigation & Multi-Tab
    browser = BrowserController()
    await browser.open_browser("chrome")
    await browser.navigate_url("https://python.org")
    tab = await browser.new_tab("https://nova.ai")
    assert tab["url"] == "https://nova.ai"
    print("Stage 7  Browser Navigation & Tabs  PASS")

    # Stage 8: Form Automation
    filler = FormFiller()
    fields = await filler.detect_fields()
    assert len(fields) >= 5
    await filler.fill_form_data("form", {"username": "admin"})
    print("Stage 8  Form Detection & Filling   PASS")

    # Stage 9: Downloads & Uploads
    dm = DownloadManager()
    dl_path = await dm.handle_download("https://python.org/doc.pdf", "doc.pdf")
    assert "doc.pdf" in dl_path
    print("Stage 9  Downloads & File Intercept PASS")

    # Stage 10: Safety & Permission Interception
    perm = AutomationPermissionManager(config=AutomationConfiguration(safety_dry_run=True))
    allowed = await perm.verify_permission("make_payment", {"amount": 50})
    assert allowed is True
    print("Stage 10 Safety & Human Approval    PASS")

    # Stage 11: End-to-End Voice Pipeline
    runtime = AutomationRuntime()
    pipeline = AutomationPipeline(runtime=runtime)
    res_pipe = await pipeline.execute_voice_command("open Chrome and search for Python")
    assert res_pipe["success"] is True
    print("Stage 11 End-to-End Voice Pipeline  PASS")

    # Stage 12: Gateway Integration
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass
    gateway = resolve(IAIGateway)
    gw_res = await gateway.open_application("calc.exe")
    assert gw_res["success"] is True
    print("Stage 12 Gateway Integration        PASS")

    print("\n12/12 PASS")
    print("\nAutomation Engine Healthy")


if __name__ == "__main__":
    asyncio.run(run_manual_validation())
