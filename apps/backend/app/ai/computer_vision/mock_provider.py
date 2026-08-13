"""Mock Vision Provider for offline unit tests and CI integration.
"""

from typing import Any, Dict, List, Optional
from app.ai.computer_vision.models import (
    AdaptiveLocatorResult,
    ApplicationProfile,
    DesktopScene,
    ElementType,
    GUIElement,
    ReasoningPurpose,
    ScreenHistoryItem,
    VisionHealth,
    VisionState,
    VisualReasoningResult,
)


class MockVisionProvider:
    """Mock Vision Provider returning deterministic test data."""

    async def analyze_screen(self, monitor_index: int = 0) -> DesktopScene:
        """Returns mock DesktopScene."""
        return DesktopScene(
            active_window_title="Mock Window",
            process_name="mock_app.exe",
            resolution={"width": 1920, "height": 1080},
            monitor_index=monitor_index,
            elements=[
                GUIElement(
                    type=ElementType.BUTTON,
                    label="Mock Button",
                    confidence=0.99,
                    bounding_box={"x": 50, "y": 50, "width": 100, "height": 30},
                    accessibility_id="btn_mock",
                )
            ],
        )

    async def find_ui_element(self, query: str, **kwargs: Any) -> AdaptiveLocatorResult:
        """Returns mock AdaptiveLocatorResult."""
        return AdaptiveLocatorResult(
            found=True,
            element=GUIElement(label=query, type=ElementType.BUTTON),
            locator_strategy="accessibility_api",
            confidence=0.99,
        )

    async def reason_about_screen(self, query: str = "") -> VisualReasoningResult:
        """Returns mock VisualReasoningResult."""
        return VisualReasoningResult(
            purpose=ReasoningPurpose.LOCATE_CONTROL,
            diagnosis=f"Mock screen diagnosis for: {query}",
            recommended_action="Click mock target button",
            confidence=0.98,
        )

    async def check_health(self) -> VisionHealth:
        """Returns mock VisionHealth."""
        return VisionHealth(
            is_healthy=True,
            vision_state=VisionState.IDLE,
            active_monitors_count=1,
            loaded_profiles=["MockProfile"],
        )
