"""Universal Computer Understanding & Adaptive GUI Intelligence package.

Exposes vision configuration, models, interfaces, exceptions, scene analyzer, GUI understanding,
visual reasoning, application profiles, adaptive locator, document OCR understanding, IDE/Browser engines,
automation recovery, screen memory, multi-monitor support, vision agent, observability, and central ComputerVisionEngine.
"""

import sys
from typing import Any
from app.ai.computer_vision.utils import lazy_import

__all__ = [
    "ComputerVisionConfiguration",
    "ElementType",
    "ReasoningPurpose",
    "VisionState",
    "GUIElement",
    "DesktopScene",
    "VisualReasoningResult",
    "ApplicationProfile",
    "AdaptiveLocatorResult",
    "DocumentStructure",
    "IDEScene",
    "BrowserScene",
    "RecoveryPlan",
    "ScreenHistoryItem",
    "VisionMetrics",
    "VisionHealth",
    "IComputerVisionEngine",
    "IDesktopSceneAnalyzer",
    "IGUIUnderstandingEngine",
    "IVisualReasoningEngine",
    "IApplicationProfileEngine",
    "IAdaptiveLocator",
    "IDocumentUnderstandingEngine",
    "IIDEUnderstandingEngine",
    "IBrowserUnderstandingEngine",
    "IAutomationRecovery",
    "IScreenMemory",
    "IMultiMonitorManager",
    "IVisionAgent",
    "IVisionManager",
    "ComputerVisionError",
    "DesktopSceneAnalyzer",
    "GUIUnderstandingEngine",
    "VisualReasoningEngine",
    "ApplicationProfileEngine",
    "AdaptiveLocator",
    "DocumentUnderstandingEngine",
    "IDEUnderstandingEngine",
    "BrowserUnderstandingEngine",
    "AutomationRecovery",
    "ScreenMemory",
    "MultiMonitorManager",
    "VisionAgent",
    "VisionMetricsTracker",
    "VisionHealthMonitor",
    "VisionCache",
    "MockVisionProvider",
    "VisionManager",
    "ComputerVisionEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
