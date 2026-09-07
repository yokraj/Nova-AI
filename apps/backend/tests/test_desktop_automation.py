"""Unit and integration tests for Universal Desktop, Browser & OS Automation Engine.
"""

import pytest
from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
from app.ai.desktop_automation.exceptions import ApprovalRequiredError
from app.ai.desktop_automation.mock_provider import MockDesktopAutomationProvider
from app.ai.desktop_automation.models import ActionStatus, AutomationPriority, ExecutionMode


@pytest.mark.anyio
async def test_launch_app_and_activate_window():
    engine = UniversalDesktopAutomationEngine()
    app_info = await engine.launch_app("VS Code")
    assert app_info.name == "VS Code"
    assert app_info.is_running is True

    win_info = await engine.activate_window("VS Code")
    assert win_info.is_active is True


@pytest.mark.anyio
async def test_semantic_gui_click_and_typing():
    engine = UniversalDesktopAutomationEngine()
    click_res = await engine.click_control("Save Button", container_window="VS Code")
    assert click_res.success is True

    type_res = await engine.type_text("print('Hello Nova')")
    assert type_res.success is True


@pytest.mark.anyio
async def test_web_browser_automation():
    engine = UniversalDesktopAutomationEngine()
    tab = await engine.open_url("https://github.com/yokraj/Nova-AI", browser="chrome")
    assert tab.url == "https://github.com/yokraj/Nova-AI"
    assert tab.is_active is True

    form_res = await engine.fill_form({"username": "user", "password": "pass_secret"})
    assert form_res.success is True


@pytest.mark.anyio
async def test_terminal_and_os_automation():
    engine = UniversalDesktopAutomationEngine()
    cmd_res = await engine.run_terminal_command("Get-Process", shell="powershell")
    assert cmd_res["exit_code"] == 0

    setting_res = await engine.configure_setting("dark_mode", True)
    assert setting_res["status"] == "CONFIGURED"


@pytest.mark.anyio
async def test_office_and_pdf_automation():
    engine = UniversalDesktopAutomationEngine()
    doc = await engine.automate_office("C:\\Users\\User\\Documents\\report.xlsx", "generate_report")
    assert doc.doc_type == "excel"
    assert doc.page_count >= 1


@pytest.mark.anyio
async def test_filesystem_operations():
    engine = UniversalDesktopAutomationEngine()
    fop = await engine.file_operation("copy", "C:\\source.txt", destination_path="C:\\dest.txt")
    assert fop.op_type == "copy"


@pytest.mark.anyio
async def test_failure_recovery_and_templates():
    engine = UniversalDesktopAutomationEngine()
    recovery = engine.automation_recovery.generate_recovery_plan("Button clicked failed")
    assert recovery.retry_recommended is True

    templates = engine.automation_templates.list_templates()
    assert len(templates) >= 1


@pytest.mark.anyio
async def test_windows_accessibility_and_uia():
    engine = UniversalDesktopAutomationEngine()
    tree = await engine.inspect_accessibility_tree("VS Code")
    assert "controls" in tree
    assert tree["children_count"] >= 1

    ctrl = engine.accessibility_engine.find_control("Save Button")
    assert ctrl.automation_id == "AutoId_Save Button"


@pytest.mark.anyio
async def test_win32_api_and_pywinauto_adapters():
    engine = UniversalDesktopAutomationEngine()
    top_windows = engine.win32_api_wrapper.enum_windows()
    assert len(top_windows) >= 1

    pwa_conn = engine.pywinauto_adapter.connect_window("VS Code")
    assert pwa_conn["status"] == "CONNECTED"


@pytest.mark.anyio
async def test_smart_waiting_engine():
    engine = UniversalDesktopAutomationEngine()
    wait_res = await engine.wait_for_condition("window_exists", "VS Code", timeout_sec=1.0)
    assert wait_res["satisfied"] is True


@pytest.mark.anyio
async def test_playwright_browser_engine():
    engine = UniversalDesktopAutomationEngine()
    tab = await engine.run_browser_playwright("https://github.com", headless=True)
    assert "github.com" in tab.url


@pytest.mark.anyio
async def test_multimodal_vision_and_ocr():
    engine = UniversalDesktopAutomationEngine()
    vis_res = engine.vision_automation_engine.locate_control_visually("Submit Button")
    assert vis_res.confidence >= 0.9

    ocr_res = engine.ocr_engine.extract_screen_text()
    assert "INVOICE" in ocr_res.detected_text


@pytest.mark.anyio
async def test_ai_planning_goal_compilation():
    engine = UniversalDesktopAutomationEngine()
    plan = await engine.execute_goal_plan("Generate monthly sales report")
    assert len(plan) >= 5
    assert plan[0].action_type == "launch_app"


@pytest.mark.anyio
async def test_security_approval_enforcement():
    engine = UniversalDesktopAutomationEngine()
    with pytest.raises(ApprovalRequiredError):
        engine.security_engine.enforce_security_check("registry_write", is_user_approved=False)


@pytest.mark.anyio
async def test_benchmarks_and_failure_analytics():
    engine = UniversalDesktopAutomationEngine()
    benchmarks = await engine.get_automation_benchmarks()
    assert benchmarks.automation_success_rate == 1.0

    engine.failure_analytics.log_failure("act_test", "Timeout")
    logs = await engine.analyze_failure_logs()
    assert len(logs) == 1


@pytest.mark.anyio
async def test_desktop_health_and_metrics():
    engine = UniversalDesktopAutomationEngine()
    health = await engine.check_health()
    assert health.is_healthy is True

    await engine.click_control("Save Button")
    metrics = await engine.get_metrics()
    assert metrics.total_actions >= 1


@pytest.mark.anyio
async def test_mock_desktop_automation_provider():
    mock = MockDesktopAutomationProvider()
    app = await mock.mock_launch_app("Chrome")
    assert app.name == "Chrome"

    click_res = await mock.mock_click_control("Submit")
    assert click_res.success is True


@pytest.mark.anyio
async def test_application_context_and_adapters():
    from app.ai.desktop_automation.application_adapter import BaseApplicationAdapter, BlenderApplicationAdapter
    from app.ai.desktop_automation.exceptions import ApprovalRequiredError
    from app.ai.desktop_automation.models import ApplicationContext, AutomationAction

    adapter = BaseApplicationAdapter("VS Code")

    # 1. Test ApplicationContext retrieval
    context = await adapter.get_context()
    assert isinstance(context, ApplicationContext)
    assert context.app_name == "VS Code"

    # 2. Test Security check occurs BEFORE execution
    sensitive_action = AutomationAction(action_type="registry_write", target_label="HKLM")
    with pytest.raises(ApprovalRequiredError):
        await adapter.execute(sensitive_action)

    # 3. Test unsupported adapter action returns success=False (never fake success)
    unsupported_action = AutomationAction(action_type="custom_unsupported_action", target_label="target")
    result_unsupported = await adapter.execute(unsupported_action)
    assert result_unsupported.success is False
    assert "not supported or implemented" in result_unsupported.error_message

    # 4. Test verification cannot turn fake/failed success into verified=True
    verification_unsupported = await adapter.verify(unsupported_action, result_unsupported)
    assert verification_unsupported.verified is False
    assert verification_unsupported.confidence == 0.0

    # 5. Test supported desktop action uses real infrastructure
    supported_action = AutomationAction(action_type="click", target_label="Save Button")
    result_supported = await adapter.execute(supported_action)
    assert result_supported.success is True
    verification_supported = await adapter.verify(supported_action, result_supported)
    assert verification_supported.verified is True

    # 6. Test Blender foundation does not claim unimplemented execution
    blender_adapter = BlenderApplicationAdapter()
    blender_unimplemented = AutomationAction(action_type="blender_render_scene", target_label="camera")
    blender_result = await blender_adapter.execute(blender_unimplemented)
    assert blender_result.success is False
    assert "Foundation Only" in blender_result.error_message

    blender_verify = await blender_adapter.verify(blender_unimplemented, blender_result)
    assert blender_verify.verified is False


