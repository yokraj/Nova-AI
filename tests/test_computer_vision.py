"""Unit and integration tests for Computer Vision & Adaptive GUI Intelligence Engine.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.computer_vision.vision_engine import ComputerVisionEngine
from app.ai.computer_vision.mock_provider import MockVisionProvider
from app.ai.computer_vision.models import (
    ElementType,
    ReasoningPurpose,
    VisionState,
)


@pytest.mark.anyio
async def test_desktop_scene_analyzer():
    engine = ComputerVisionEngine()
    scene = await engine.analyze_screen()
    assert scene.active_window_title != ""
    assert len(scene.elements) >= 3
    elem_types = [e.type.value for e in scene.elements]
    assert "button" in elem_types
    assert "text_field" in elem_types


@pytest.mark.anyio
async def test_gui_understanding_engine():
    engine = ComputerVisionEngine()
    scene = await engine.desktop_analyzer.analyze_desktop()
    classified = await engine.gui_understanding.parse_gui_elements(scene)
    assert len(classified) == len(scene.elements)
    save_btn = next((e for e in classified if e.label == "Save"), None)
    assert save_btn is not None
    assert save_btn.confidence >= 0.95


@pytest.mark.anyio
async def test_visual_reasoning_engine():
    engine = ComputerVisionEngine()
    res = await engine.reason_about_screen("automation error stopped execution")
    assert res.purpose == ReasoningPurpose.AUTOMATION_RECOVERY
    assert len(res.recovery_steps) > 0
    assert res.target_element is not None


@pytest.mark.anyio
async def test_application_profiles():
    engine = ComputerVisionEngine()
    chrome_prof = await engine.understand_application("Chrome")
    assert "chrome.exe" in chrome_prof.process_names
    assert "navigate_url" in chrome_prof.expected_workflows

    vscode_prof = await engine.understand_application("VS Code")
    assert "code.exe" in vscode_prof.process_names
    assert "File" in vscode_prof.known_menus


@pytest.mark.anyio
async def test_adaptive_locator():
    engine = ComputerVisionEngine()
    loc_res = await engine.find_ui_element("btn_save")
    assert loc_res.found is True
    assert loc_res.locator_strategy in ["accessibility_api", "accessibility_label"]
    assert loc_res.element is not None


@pytest.mark.anyio
async def test_document_understanding():
    engine = ComputerVisionEngine()
    doc_struct = await engine.document_understanding.parse_document("financial_report.pdf")
    assert doc_struct.page_count >= 1
    assert len(doc_struct.tables) > 0
    assert "total_due" in doc_struct.forms


@pytest.mark.anyio
async def test_ide_and_browser_understanding():
    engine = ComputerVisionEngine()
    ide_scene = await engine.ide_understanding.analyze_ide_screen()
    assert ide_scene.active_file == "apps/backend/app/ai/computer_vision/ide_understanding.py"

    web_scene = await engine.browser_understanding.analyze_browser_page("https://github.com/yokraj/Nova-AI")
    assert web_scene.page_purpose == "code_repository_navigation"
    assert len(web_scene.tables) > 0


@pytest.mark.anyio
async def test_automation_recovery():
    engine = ComputerVisionEngine()
    scene = await engine.desktop_analyzer.analyze_desktop()
    rec_plan = await engine.automation_recovery.recover_automation("click Save button", scene)
    assert rec_plan.verified is True
    assert rec_plan.alternative_element is not None


@pytest.mark.anyio
async def test_screen_memory_and_multi_monitor():
    engine = ComputerVisionEngine()
    await engine.analyze_screen()
    hist = await engine.screen_history()
    assert len(hist) > 0

    monitors = engine.multi_monitor.list_monitors()
    assert len(monitors) >= 2
    trans = engine.multi_monitor.transform_coordinates(100, 100, 0, 1)
    assert "global_x" in trans


@pytest.mark.anyio
async def test_vision_agent():
    engine = ComputerVisionEngine()
    res = await engine.vision_agent.execute_visual_task("Explain architecture diagram")
    assert res["status"] == "completed"
    assert "diagram_structure" in res


@pytest.mark.anyio
async def test_mock_vision_provider():
    mock = MockVisionProvider()
    scene = await mock.analyze_screen()
    assert scene.process_name == "mock_app.exe"
    health = await mock.check_health()
    assert health.is_healthy is True
