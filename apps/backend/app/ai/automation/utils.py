"""PEP 562 Lazy Import Utility Mapping for the Automation package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core Config & Models
    "AutomationConfiguration": "app.ai.automation.configuration",
    "AutomationState": "app.ai.automation.models",
    "ActionType": "app.ai.automation.models",
    "BrowserType": "app.ai.automation.models",
    "TargetPlatform": "app.ai.automation.models",
    "WindowAction": "app.ai.automation.models",
    "UIElement": "app.ai.automation.models",
    "WindowInfo": "app.ai.automation.models",
    "ProcessInfo": "app.ai.automation.models",
    "OCRResult": "app.ai.automation.models",
    "ImageMatch": "app.ai.automation.models",
    "AutomationRequest": "app.ai.automation.models",
    "AutomationResult": "app.ai.automation.models",
    "AutomationMetrics": "app.ai.automation.models",
    "AutomationHealth": "app.ai.automation.models",
    # Interfaces
    "IDesktopController": "app.ai.automation.interfaces",
    "IBrowserController": "app.ai.automation.interfaces",
    "IOCREngine": "app.ai.automation.interfaces",
    "IFormFiller": "app.ai.automation.interfaces",
    "IAutomationRuntime": "app.ai.automation.interfaces",
    # Exceptions
    "AutomationError": "app.ai.automation.exceptions",
    "DesktopError": "app.ai.automation.exceptions",
    "BrowserError": "app.ai.automation.exceptions",
    "WindowNotFoundError": "app.ai.automation.exceptions",
    "ElementNotFoundError": "app.ai.automation.exceptions",
    "OCRProcessingError": "app.ai.automation.exceptions",
    "AutomationSafetyError": "app.ai.automation.exceptions",
    # Desktop Sub-systems
    "WindowManager": "app.ai.automation.window_manager",
    "MouseController": "app.ai.automation.mouse_controller",
    "KeyboardController": "app.ai.automation.keyboard_controller",
    "ClipboardManager": "app.ai.automation.clipboard_manager",
    "ScreenCapture": "app.ai.automation.screen_capture",
    "OCREngine": "app.ai.automation.ocr_engine",
    "ImageLocator": "app.ai.automation.image_locator",
    "UIElementDetector": "app.ai.automation.ui_element_detector",
    "ApplicationLauncher": "app.ai.automation.application_launcher",
    "ProcessManager": "app.ai.automation.process_manager",
    "DesktopController": "app.ai.automation.desktop_controller",
    # Browser Sub-systems
    "BrowserProfiles": "app.ai.automation.browser_profiles",
    "BrowserSession": "app.ai.automation.browser_session",
    "TabManager": "app.ai.automation.tab_manager",
    "DownloadManager": "app.ai.automation.download_manager",
    "UploadManager": "app.ai.automation.upload_manager",
    "NavigationEngine": "app.ai.automation.navigation_engine",
    "FormFiller": "app.ai.automation.form_filler",
    "DOMInspector": "app.ai.automation.dom_inspector",
    "JavaScriptExecutor": "app.ai.automation.javascript_executor",
    "SelectorEngine": "app.ai.automation.selector_engine",
    "CookieManager": "app.ai.automation.cookie_manager",
    "HistoryManager": "app.ai.automation.history_manager",
    "BrowserController": "app.ai.automation.browser_controller",
    # Runtime & Pipeline
    "AutomationPermissionManager": "app.ai.automation.permission_manager",
    "AutomationPipeline": "app.ai.automation.automation_pipeline",
    "AutomationRuntime": "app.ai.automation.automation_runtime",
    "AutomationScheduler": "app.ai.automation.automation_scheduler",
    "AutomationContext": "app.ai.automation.automation_context",
    "AutomationMetricsTracker": "app.ai.automation.metrics",
    "AutomationHealthMonitor": "app.ai.automation.health",
    "AutomationCache": "app.ai.automation.cache",
    "MockAutomationProvider": "app.ai.automation.providers.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in automation lazy mapping.")
