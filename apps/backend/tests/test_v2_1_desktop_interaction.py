"""NOVA AI V2.1 — Real Desktop Interaction and Native Bridge Test Suite.

Verifies:
1. Native Bridge connection, health checks, timeouts, and recovery
2. Window management tools: list_windows, get_active_window, focus_window, close_window
3. Keyboard interaction tools: keyboard_type, keyboard_press, keyboard_combination
4. Mouse interaction tools: mouse_move, mouse_click
5. Screen understanding: capture_screenshot
6. Security permissions and honest offline reporting
7. End-to-end multi-step desktop task planning
"""

import sys
from pathlib import Path
import pytest
import pytest_asyncio

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.ai.desktop_automation.native_bridge_client import NativeBridgeClient
from app.intelligence.unified_tool_registry import (
    UnifiedToolRegistry,
    ToolPermissionLevel,
)
from app.intelligence.agent_execution_engine import (
    AgentExecutionEngine,
    TaskIntent,
    StepStatus,
)
from app.security.workspace_guard import WorkspaceSecurityGuard
from app.ai.desktop_automation.security_engine import SecurityEngine


@pytest.fixture
def workspace_guard() -> WorkspaceSecurityGuard:
    return WorkspaceSecurityGuard(root_dir=BASE_DIR.parent.parent)


@pytest.fixture
def bridge_client() -> NativeBridgeClient:
    return NativeBridgeClient(base_url="http://127.0.0.1:3001")


@pytest.fixture
def tool_registry(workspace_guard: WorkspaceSecurityGuard, bridge_client: NativeBridgeClient) -> UnifiedToolRegistry:
    return UnifiedToolRegistry(
        workspace_guard=workspace_guard,
        bridge_client=bridge_client,
    )


@pytest.fixture
def engine(tool_registry: UnifiedToolRegistry, workspace_guard: WorkspaceSecurityGuard) -> AgentExecutionEngine:
    return AgentExecutionEngine(
        tool_registry=tool_registry,
        workspace_guard=workspace_guard,
    )


# =============================================================================
# Phase 1: Native Bridge Connection & Robustness Tests
# =============================================================================
def test_bridge_health_check(bridge_client: NativeBridgeClient):
    """Verifies Native Bridge health endpoint."""
    health = bridge_client.check_health()
    assert isinstance(health, dict)
    if health.get("healthy"):
        assert health["data"].get("status") == "healthy"
        assert health["data"].get("service") == "nova-native-bridge"
    else:
        assert "error" in health


def test_bridge_offline_honest_reporting():
    """Verifies that client connecting to invalid port reports honest failure."""
    dead_client = NativeBridgeClient(base_url="http://127.0.0.1:49999", default_timeout=1.0)
    assert dead_client.is_available() is False
    res = dead_client.execute_native(
        capability="COMPUTER_CONTROL",
        action="WINDOW_GET_ACTIVE",
    )
    assert res.get("status") == "FAILED"
    assert res.get("verification") == "VERIFICATION_FAILED"
    assert res.get("errorReason") in ("NATIVE_BRIDGE_OFFLINE", "EXECUTION_TIMEOUT")


# =============================================================================
# Phase 2: Real Desktop Control Tools in Unified Tool Registry
# =============================================================================
def test_desktop_tools_registered(tool_registry: UnifiedToolRegistry):
    """Verifies all Phase 2 desktop control tools are registered with schemas."""
    expected_tools = [
        "list_windows",
        "get_active_window",
        "focus_window",
        "close_window",
        "keyboard_type",
        "keyboard_press",
        "keyboard_combination",
        "mouse_move",
        "mouse_click",
        "capture_screenshot",
    ]
    for tool_name in expected_tools:
        tool = tool_registry.get(tool_name)
        assert tool is not None, f"Tool '{tool_name}' must be registered."
        schema = tool.to_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == tool_name
        assert "parameters" in schema["function"]


@pytest.mark.asyncio
async def test_tool_list_windows(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies list_windows tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool("list_windows", {})
    assert res.success is True
    assert res.verified is True
    assert isinstance(res.output.get("windows"), list)


@pytest.mark.asyncio
async def test_tool_get_active_window(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies get_active_window tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool("get_active_window", {})
    assert res.success is True
    assert res.verified is True
    assert "active_window" in res.output


@pytest.mark.asyncio
async def test_tool_keyboard_type(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies keyboard_type execution and verification."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool(
        "keyboard_type",
        {"text": "Nova Test Typing"},
        is_user_approved=True,
    )
    assert res.success is True
    assert res.verified is True
    assert res.output.get("typed_length") == len("Nova Test Typing")


@pytest.mark.asyncio
async def test_tool_keyboard_press(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies keyboard_press tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool(
        "keyboard_press",
        {"key_name": "enter"},
        is_user_approved=True,
    )
    assert res.success is True
    assert res.verified is True
    assert res.output.get("key_name") == "enter"


@pytest.mark.asyncio
async def test_tool_keyboard_combination(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies keyboard_combination tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool(
        "keyboard_combination",
        {"keys": ["ctrl", "c"]},
        is_user_approved=True,
    )
    assert res.success is True
    assert res.verified is True
    assert res.output.get("keys") == ["ctrl", "c"]


@pytest.mark.asyncio
async def test_tool_mouse_move(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies mouse_move tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool(
        "mouse_move",
        {"x": 450, "y": 350},
    )
    assert res.success is True
    assert res.verified is True
    assert res.output.get("x") == 450
    assert res.output.get("y") == 350


@pytest.mark.asyncio
async def test_tool_mouse_click(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient):
    """Verifies mouse_click tool execution."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    res = await tool_registry.execute_tool(
        "mouse_click",
        {"x": 450, "y": 350, "button": "left"},
        is_user_approved=True,
    )
    assert res.success is True
    assert res.verified is True


@pytest.mark.asyncio
async def test_tool_capture_screenshot(tool_registry: UnifiedToolRegistry, bridge_client: NativeBridgeClient, workspace_guard: WorkspaceSecurityGuard):
    """Verifies capture_screenshot creates verified image file in workspace."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    target_rel = "screenshots/test_suite_capture.png"
    res = await tool_registry.execute_tool(
        "capture_screenshot",
        {"save_path": target_rel},
    )
    assert res.success is True
    assert res.verified is True
    assert "file_path" in res.output
    saved_file = workspace_guard.resolve_workspace_path(target_rel)
    assert saved_file.exists() is True
    assert saved_file.stat().st_size > 0
    # Clean up test artifact
    saved_file.unlink(missing_ok=True)


# =============================================================================
# Phase 3 & 4: Multi-Step Task Planning for Real Desktop Automation
# =============================================================================
def test_desktop_interaction_plan_creation(engine: AgentExecutionEngine):
    """Verifies that explicit save requests create physical desktop sequence."""
    prompt = "Open Notepad, create a file named meeting.txt, write Tomorrow's meeting is at 10 AM, save the file, and verify the contents."
    analysis = engine.understand_task(prompt)
    assert analysis["intent"] == TaskIntent.MULTI_STEP_TASK
    assert analysis["entities"]["app_name"] == "Notepad"
    assert "Tomorrow's meeting is at 10 AM" in analysis["entities"]["content"]

    plan = engine.create_plan(prompt, analysis)
    # Must use physical keyboard and window tools
    tool_names = [s.tool_name for s in plan.steps]
    assert "open_application" in tool_names
    assert "focus_window" in tool_names
    assert "keyboard_type" in tool_names
    assert "keyboard_combination" in tool_names
    assert "keyboard_press" in tool_names
    assert "read_document" in tool_names
    assert "create_file" not in tool_names  # Confirms create_file was NOT used as a shortcut!


@pytest.mark.asyncio
async def test_phase_4_real_notepad_acceptance_execution(
    engine: AgentExecutionEngine,
    bridge_client: NativeBridgeClient,
    workspace_guard: WorkspaceSecurityGuard,
):
    """Phase 4 Acceptance Test:
    User request: 'Open Notepad, create a file named meeting.txt, write Tomorrow's meeting is at 10 AM, save the file, and verify the contents.'
    Executes real keyboard typing, shortcut save, disk verification, and clean shutdown.
    """
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    prompt = "Open Notepad, create a file named meeting.txt, write Tomorrow's meeting is at 10 AM, save the file, and verify the contents."
    target_disk_file = workspace_guard.resolve_workspace_path("meeting.txt")
    target_disk_file.unlink(missing_ok=True)

    try:
        analysis = engine.understand_task(prompt)
        plan = engine.create_plan(prompt, analysis)
        report = await engine.execute_plan(plan, is_user_approved=True)

        assert report.status == "SUCCEEDED"
        assert report.verified is True
        assert report.steps_succeeded == len(plan.steps)
        assert target_disk_file.exists() is True
        file_content = target_disk_file.read_text(encoding="utf-8")
        assert "Tomorrow's meeting is at 10 AM" in file_content
    finally:
        target_disk_file.unlink(missing_ok=True)
        engine.tools.launcher.terminate_application("notepad")


@pytest.mark.asyncio
async def test_phase_5_calculator_validation(
    engine: AgentExecutionEngine,
    bridge_client: NativeBridgeClient,
):
    """Phase 5: Multi-application test for Calculator."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    try:
        # Launch Calculator
        launch_res = await engine.tools.execute_tool("open_application", {"app_name": "calc"}, is_user_approved=True)
        assert launch_res.success is True
        assert launch_res.verified is True
        assert engine.tools.launcher.is_application_running("calc") is True

        # Focus Calculator
        focus_res = await engine.tools.execute_tool("focus_window", {"target_name": "calc"}, is_user_approved=True)
        assert focus_res.success is True
    finally:
        # Close Calculator
        await engine.tools.execute_tool("close_application", {"app_name": "calc"}, is_user_approved=True)


@pytest.mark.asyncio
async def test_phase_5_window_switching_validation(
    engine: AgentExecutionEngine,
    bridge_client: NativeBridgeClient,
):
    """Phase 5: Multi-application window switching verification."""
    if not bridge_client.is_available():
        pytest.skip("Native Bridge server not running on port 3001")

    try:
        # Launch Notepad
        await engine.tools.execute_tool("open_application", {"app_name": "notepad"}, is_user_approved=True)
        # Focus Notepad
        focus1 = await engine.tools.execute_tool("focus_window", {"target_name": "notepad"}, is_user_approved=True)
        assert focus1.success is True

        # Launch Calculator
        await engine.tools.execute_tool("open_application", {"app_name": "calc"}, is_user_approved=True)
        # Focus Calculator
        focus2 = await engine.tools.execute_tool("focus_window", {"target_name": "calc"}, is_user_approved=True)
        assert focus2.success is True

        # Switch back to Notepad
        focus3 = await engine.tools.execute_tool("focus_window", {"target_name": "notepad"}, is_user_approved=True)
        assert focus3.success is True
    finally:
        engine.tools.launcher.terminate_application("calc")
        engine.tools.launcher.terminate_application("notepad")

