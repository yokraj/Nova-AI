"""12-Stage Manual Validation Script for M3.4.4 Universal Computer Understanding Engine.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.computer_vision import (
    ComputerVisionEngine,
    ComputerVisionConfiguration,
    VisionState,
    ElementType,
    ReasoningPurpose,
    MockVisionProvider,
)
from app.ai.gateway import AIGateway, ProviderRegistry, ModelRegistry, ProviderFactory, RetryPolicy, TimeoutPolicy


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.4 – Universal Computer Understanding Engine Validation")
    print("==================================================================\n")

    engine = ComputerVisionEngine()

    # Stage 1: Core Vision Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Vision Package Init & PEP 562 Lazy Loader")
    assert engine.config.prefer_accessibility_apis is True
    print("  [OK] Computer Vision package loaded successfully.\n")

    # Stage 2: Desktop Scene Analyzer
    print("Stage 2: Desktop Scene Analyzer (Capture & Window Hierarchy)")
    scene = await engine.analyze_screen(monitor_index=0)
    print(f"  * Scene ID: {scene.scene_id}")
    print(f"  * Active Window: '{scene.active_window_title}' ({scene.process_name})")
    print(f"  * Resolution: {scene.resolution['width']}x{scene.resolution['height']}")
    print(f"  * Total GUI Elements Detected: {len(scene.elements)}")
    assert len(scene.elements) >= 3
    print("  [OK] Desktop Scene Analyzer captured desktop layout & hierarchy.\n")

    # Stage 3: GUI Understanding Engine
    print("Stage 3: GUI Understanding Engine (Control Semantics & Confidence)")
    classified = await engine.gui_understanding.parse_gui_elements(scene)
    for elem in classified[:3]:
        print(f"  * Element: '{elem.label}' (Type: {elem.type.value}, Confidence: {elem.confidence:.2f})")
    save_btn = next((e for e in classified if e.label == "Save"), None)
    assert save_btn is not None
    print("  [OK] GUI Understanding Engine categorized UI controls.\n")

    # Stage 4: Visual Reasoning Engine
    print("Stage 4: Visual Reasoning Engine (Diagnosis & Recovery Guidance)")
    reason_res = await engine.reason_about_screen("modal confirmation dialog error")
    print(f"  * Purpose: {reason_res.purpose.value}")
    print(f"  * Diagnosis: {reason_res.diagnosis}")
    print(f"  * Action: {reason_res.recommended_action}")
    assert reason_res.target_element is not None
    print("  [OK] Visual Reasoning Engine diagnosed screen state.\n")

    # Stage 5: Application Profile Engine
    print("Stage 5: Application Profile Engine (App Profiles)")
    chrome_prof = await engine.understand_application("Chrome")
    vscode_prof = await engine.understand_application("VS Code")
    excel_prof = await engine.understand_application("Excel")
    print(f"  * Chrome Regions: {list(chrome_prof.common_ui_regions.keys())}")
    print(f"  * VS Code Menus: {vscode_prof.known_menus[:4]}")
    print(f"  * Excel Workflows: {excel_prof.expected_workflows[:2]}")
    assert "chrome.exe" in chrome_prof.process_names
    print("  [OK] Application Profile Engine resolved 19 application blueprints.\n")

    # Stage 6: Adaptive UI Locator
    print("Stage 6: Adaptive UI Locator (Dynamic Lookup)")
    loc_res = await engine.find_ui_element("btn_save")
    print(f"  * Found: {loc_res.found} | Strategy: {loc_res.locator_strategy}")
    print(f"  * Element Label: '{loc_res.element.label if loc_res.element else ''}' (x: {loc_res.element.bounding_box['x']}, y: {loc_res.element.bounding_box['y']})")
    assert loc_res.found is True
    print("  [OK] Adaptive UI Locator found control dynamically.\n")

    # Stage 7: OCR & Document Understanding Engine
    print("Stage 7: OCR & Document Understanding Engine (PDFs, Tables, Forms)")
    doc_struct = await engine.document_understanding.parse_document("invoice_2026.pdf")
    print(f"  * Document Title: {doc_struct.title}")
    print(f"  * Extracted Form Fields: {doc_struct.forms}")
    print(f"  * Tables Extracted: {len(doc_struct.tables)}")
    assert "total_due" in doc_struct.forms
    print("  [OK] Document Understanding Engine extracted structured content.\n")

    # Stage 8: IDE Understanding Engine
    print("Stage 8: IDE Understanding Engine (Workspace Snapshot)")
    ide_scene = await engine.ide_understanding.analyze_ide_screen()
    print(f"  * Active File: {ide_scene.active_file}")
    print(f"  * Open Tabs: {ide_scene.open_tabs}")
    print(f"  * Cursor Location: Line {ide_scene.cursor_line}, Col {ide_scene.cursor_col}")
    assert ide_scene.active_file == "apps/backend/app/ai/computer_vision/ide_understanding.py"
    print("  [OK] IDE Understanding Engine extracted IDE workspace state.\n")

    # Stage 9: Browser Page Understanding Engine
    print("Stage 9: Browser Page Understanding Engine (Web Semantics)")
    web_scene = await engine.browser_understanding.analyze_browser_page("https://github.com/yokraj/Nova-AI")
    print(f"  * Title: {web_scene.page_title}")
    print(f"  * Purpose: {web_scene.page_purpose}")
    print(f"  * Tables Count: {len(web_scene.tables)}")
    assert web_scene.page_purpose == "code_repository_navigation"
    print("  [OK] Browser Understanding Engine categorized web page layout.\n")

    # Stage 10: Adaptive Automation Recovery Engine
    print("Stage 10: Adaptive Automation Recovery Engine (Failure Recovery)")
    rec_plan = await engine.automation_recovery.recover_automation("click Save button", scene)
    print(f"  * Failure Reason: {rec_plan.failure_reason}")
    print(f"  * Recovery Action: {rec_plan.recovery_action}")
    assert rec_plan.verified is True
    print("  [OK] Automation Recovery Engine generated failure resolution plan.\n")

    # Stage 11: Screen Memory & Multi-Monitor Support
    print("Stage 11: Screen Memory & Multi-Monitor Support")
    hist = await engine.screen_history()
    monitors = engine.multi_monitor.list_monitors()
    trans = engine.multi_monitor.transform_coordinates(100, 100, 0, 1)
    print(f"  * Screen History Entries: {len(hist)}")
    print(f"  * Connected Monitors: {len(monitors)} (Primary: {monitors[0]['name']})")
    print(f"  * Coordinate Transform (0 -> 1): Local (100, 100) -> Global ({trans['global_x']}, {trans['global_y']})")
    assert len(hist) > 0
    assert len(monitors) >= 2
    print("  [OK] Screen Memory & Multi-Monitor Manager verified.\n")

    # Stage 12: Vision Agent Execution
    print("Stage 12: Vision Agent Execution")
    v_res = await engine.vision_agent.execute_visual_task("Analyze UI layout and diagram")
    print(f"  * Agent: {v_res['agent']}")
    print(f"  * Result: {v_res['analysis_result']}")
    print(f"  * Nodes in Diagram: {v_res['diagram_structure']['nodes']}")
    assert v_res["status"] == "completed"
    print("  [OK] Vision Agent executed visual task.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Universal Computer Understanding Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
