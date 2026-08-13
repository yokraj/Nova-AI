"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.computer_vision.
"""

import importlib
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "ComputerVisionConfiguration": "app.ai.computer_vision.configuration",
    "ElementType": "app.ai.computer_vision.models",
    "ReasoningPurpose": "app.ai.computer_vision.models",
    "VisionState": "app.ai.computer_vision.models",
    "GUIElement": "app.ai.computer_vision.models",
    "DesktopScene": "app.ai.computer_vision.models",
    "VisualReasoningResult": "app.ai.computer_vision.models",
    "ApplicationProfile": "app.ai.computer_vision.models",
    "AdaptiveLocatorResult": "app.ai.computer_vision.models",
    "DocumentStructure": "app.ai.computer_vision.models",
    "IDEScene": "app.ai.computer_vision.models",
    "BrowserScene": "app.ai.computer_vision.models",
    "RecoveryPlan": "app.ai.computer_vision.models",
    "ScreenHistoryItem": "app.ai.computer_vision.models",
    "VisionMetrics": "app.ai.computer_vision.models",
    "VisionHealth": "app.ai.computer_vision.models",
    "IComputerVisionEngine": "app.ai.computer_vision.interfaces",
    "IDesktopSceneAnalyzer": "app.ai.computer_vision.interfaces",
    "IGUIUnderstandingEngine": "app.ai.computer_vision.interfaces",
    "IVisualReasoningEngine": "app.ai.computer_vision.interfaces",
    "IApplicationProfileEngine": "app.ai.computer_vision.interfaces",
    "IAdaptiveLocator": "app.ai.computer_vision.interfaces",
    "IDocumentUnderstandingEngine": "app.ai.computer_vision.interfaces",
    "IIDEUnderstandingEngine": "app.ai.computer_vision.interfaces",
    "IBrowserUnderstandingEngine": "app.ai.computer_vision.interfaces",
    "IAutomationRecovery": "app.ai.computer_vision.interfaces",
    "IScreenMemory": "app.ai.computer_vision.interfaces",
    "IMultiMonitorManager": "app.ai.computer_vision.interfaces",
    "IVisionAgent": "app.ai.computer_vision.interfaces",
    "IVisionManager": "app.ai.computer_vision.interfaces",
    "ComputerVisionError": "app.ai.computer_vision.exceptions",
    "DesktopSceneAnalyzer": "app.ai.computer_vision.desktop_scene_analyzer",
    "GUIUnderstandingEngine": "app.ai.computer_vision.gui_understanding",
    "VisualReasoningEngine": "app.ai.computer_vision.visual_reasoning",
    "ApplicationProfileEngine": "app.ai.computer_vision.application_profiles",
    "AdaptiveLocator": "app.ai.computer_vision.adaptive_locator",
    "DocumentUnderstandingEngine": "app.ai.computer_vision.document_understanding",
    "IDEUnderstandingEngine": "app.ai.computer_vision.ide_understanding",
    "BrowserUnderstandingEngine": "app.ai.computer_vision.browser_understanding",
    "AutomationRecovery": "app.ai.computer_vision.automation_recovery",
    "ScreenMemory": "app.ai.computer_vision.screen_memory",
    "MultiMonitorManager": "app.ai.computer_vision.multi_monitor",
    "VisionAgent": "app.ai.computer_vision.vision_agent",
    "VisionMetricsTracker": "app.ai.computer_vision.metrics",
    "VisionHealthMonitor": "app.ai.computer_vision.health",
    "VisionCache": "app.ai.computer_vision.cache",
    "MockVisionProvider": "app.ai.computer_vision.mock_provider",
    "VisionManager": "app.ai.computer_vision.vision_manager",
    "ComputerVisionEngine": "app.ai.computer_vision.vision_engine",
}


def lazy_import(name: str) -> Any:
    """Lazy imports a symbol based on the module map.

    Args:
        name: Name of symbol to import.

    Returns:
        The imported symbol object.
    """
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module 'app.ai.computer_vision' has no attribute '{name}'")


def calculate_bounding_box_center(bbox: Dict[str, int]) -> Dict[str, int]:
    """Calculates center coordinate (x, y) for a bounding box.

    Args:
        bbox: Bounding box dict with x, y, width, height.

    Returns:
        Dict with x, y center.
    """
    return {
        "x": bbox.get("x", 0) + bbox.get("width", 0) // 2,
        "y": bbox.get("y", 0) + bbox.get("height", 0) // 2,
    }
