"""Central Computer Vision Engine orchestrating computer understanding and adaptive GUI intelligence.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.computer_vision.adaptive_locator import AdaptiveLocator
from app.ai.computer_vision.application_profiles import ApplicationProfileEngine
from app.ai.computer_vision.automation_recovery import AutomationRecovery
from app.ai.computer_vision.browser_understanding import BrowserUnderstandingEngine
from app.ai.computer_vision.configuration import ComputerVisionConfiguration
from app.ai.computer_vision.desktop_scene_analyzer import DesktopSceneAnalyzer
from app.ai.computer_vision.document_understanding import DocumentUnderstandingEngine
from app.ai.computer_vision.gui_understanding import GUIUnderstandingEngine
from app.ai.computer_vision.health import VisionHealthMonitor
from app.ai.computer_vision.ide_understanding import IDEUnderstandingEngine
from app.ai.computer_vision.interfaces import IComputerVisionEngine
from app.ai.computer_vision.metrics import VisionMetricsTracker
from app.ai.computer_vision.models import (
    AdaptiveLocatorResult,
    ApplicationProfile,
    BrowserScene,
    DesktopScene,
    DocumentStructure,
    GUIElement,
    IDEScene,
    ReasoningPurpose,
    RecoveryPlan,
    ScreenHistoryItem,
    VisionHealth,
    VisionMetrics,
    VisionState,
    VisualReasoningResult,
)
from app.ai.computer_vision.multi_monitor import MultiMonitorManager
from app.ai.computer_vision.screen_memory import ScreenMemory
from app.ai.computer_vision.vision_agent import VisionAgent
from app.ai.computer_vision.vision_manager import VisionManager
from app.ai.computer_vision.visual_reasoning import VisualReasoningEngine


class ComputerVisionEngine(IComputerVisionEngine):
    """The central Universal Computer Understanding Engine runtime for Nova AI."""

    def __init__(self, config: Optional[ComputerVisionConfiguration] = None) -> None:
        self.config = config or ComputerVisionConfiguration()
        self.manager = VisionManager(self.config)
        self.desktop_analyzer = DesktopSceneAnalyzer()
        self.gui_understanding = GUIUnderstandingEngine()
        self.visual_reasoning = VisualReasoningEngine()
        self.application_profiles = ApplicationProfileEngine()
        self.adaptive_locator = AdaptiveLocator()
        self.document_understanding = DocumentUnderstandingEngine()
        self.ide_understanding = IDEUnderstandingEngine()
        self.browser_understanding = BrowserUnderstandingEngine()
        self.automation_recovery = AutomationRecovery()
        self.screen_memory_store = ScreenMemory(limit=self.config.screen_memory_limit)
        self.multi_monitor = MultiMonitorManager()
        self.vision_agent = VisionAgent()
        self.metrics_tracker = VisionMetricsTracker()
        self.health_monitor = VisionHealthMonitor()

        self.health_monitor.set_state(VisionState.IDLE)

    async def analyze_screen(self, monitor_index: int = 0) -> DesktopScene:
        """Captures active screen layout and identifies interactive elements.

        Args:
            monitor_index: Monitor index to analyze.

        Returns:
            DesktopScene model.
        """
        start_time = time.time()
        self.health_monitor.set_state(VisionState.CAPTURING)

        scene = await self.desktop_analyzer.analyze_desktop(monitor_index=monitor_index)
        self.health_monitor.set_state(VisionState.ANALYZING)

        classified_elements = await self.gui_understanding.parse_gui_elements(scene)
        scene.elements = classified_elements

        await self.screen_memory_store.record_screen(scene, action="analyze_screen")

        elapsed_ms = (time.time() - start_time) * 1000.0
        self.metrics_tracker.record_screen_analyzed(len(scene.elements), elapsed_ms)
        self.health_monitor.set_state(VisionState.IDLE)

        return scene

    async def understand_application(self, app_name: str) -> ApplicationProfile:
        """Retrieves layout profile for target application."""
        return await self.application_profiles.get_profile(app_name)

    async def find_ui_element(self, query: str, **kwargs: Any) -> AdaptiveLocatorResult:
        """Finds UI control dynamically using accessibility APIs, DOM, or OCR.

        Args:
            query: Label or accessibility ID.
            **kwargs: Extra locator options.

        Returns:
            AdaptiveLocatorResult model.
        """
        self.health_monitor.set_state(VisionState.LOCATING)
        scene = await self.desktop_analyzer.analyze_desktop()
        res = await self.adaptive_locator.locate_element(query, scene)
        self.health_monitor.set_state(VisionState.IDLE)
        return res

    async def reason_about_screen(self, query: str = "") -> VisualReasoningResult:
        """Performs visual reasoning over current screen screenshot.

        Args:
            query: Reasoning question or purpose context.

        Returns:
            VisualReasoningResult model.
        """
        self.health_monitor.set_state(VisionState.REASONING)
        scene = await self.desktop_analyzer.analyze_desktop()
        purpose = ReasoningPurpose.AUTOMATION_RECOVERY if "error" in query.lower() or "stop" in query.lower() else ReasoningPurpose.LOCATE_CONTROL
        res = await self.visual_reasoning.reason_about_screen(scene, purpose)
        self.health_monitor.set_state(VisionState.IDLE)
        return res

    async def capture_desktop(self) -> DesktopScene:
        """Captures full desktop scene snapshot."""
        return await self.analyze_screen(monitor_index=0)

    async def capture_window(self, window_title: str) -> DesktopScene:
        """Captures specific window scene."""
        scene = await self.analyze_screen(monitor_index=0)
        scene.active_window_title = window_title
        return scene

    async def capture_region(self, x: int, y: int, width: int, height: int) -> DesktopScene:
        """Captures region bounding box."""
        scene = await self.analyze_screen(monitor_index=0)
        scene.resolution = {"width": width, "height": height}
        return scene

    async def screen_history(self) -> List[ScreenHistoryItem]:
        """Retrieves screen memory audit trail."""
        return await self.screen_memory_store.get_history(limit=10)

    async def check_health(self) -> VisionHealth:
        """Retrieves vision health monitor diagnostics."""
        return self.health_monitor.check_health()

    async def get_metrics(self) -> VisionMetrics:
        """Retrieves vision telemetry metrics."""
        return self.metrics_tracker.get_metrics()
