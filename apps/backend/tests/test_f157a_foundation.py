"""Tests for Nova-AI F1.57-A Universal Framework Foundations.

Covers:
- WindowTracker real Win32 foreground window detection & focus history
- ApplicationIdentity & ApplicationState domain abstractions
- VerificationEngine de-syntheticized state comparison
- Extended IApplicationAdapter & BaseApplicationAdapter contracts
- BlenderApplicationAdapter security enforcement (rejecting raw Python)
- 5-Tier AutomationRouter decision logic & routing
- NativeBridgeClient Python IPC client
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from app.ai.desktop_automation.models import (
    ApplicationIdentity,
    ApplicationState,
    AutomationAction,
    AutomationPriority,
    AutomationResult,
)
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.verification_engine import VerificationEngine
from app.ai.desktop_automation.application_adapter import (
    BaseApplicationAdapter,
    BlenderApplicationAdapter,
    ApplicationAdapterRegistry,
)
from app.ai.desktop_automation.automation_router import (
    AutomationRouter,
    AutomationTier,
    RouteDecision,
)
from app.ai.desktop_automation.native_bridge_client import NativeBridgeClient
from app.ai.desktop_automation.win32_api_wrapper import Win32ApiWrapper


class TestWindowTracker:
    """Test WindowTracker real Win32 foreground window tracking."""

    def test_get_active_window_real(self):
        tracker = WindowTracker()
        info = tracker.get_active_window_info()
        assert info is not None
        assert "title" in info
        assert "handle" in info
        assert "process_id" in info
        assert isinstance(info["process_id"], int)

    def test_focus_history_tracking(self):
        tracker = WindowTracker(history_size=5)
        tracker.get_active_window_info()
        history = tracker.get_focus_history()
        assert isinstance(history, list)


class TestApplicationDomainModels:
    """Test ApplicationIdentity and ApplicationState domain abstractions."""

    def test_application_identity(self):
        identity = ApplicationIdentity(
            app_name="blender",
            executable_name="blender.exe",
            executable_path=r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        )
        assert identity.app_name == "blender"
        assert identity.executable_name == "blender.exe"

    def test_application_state(self):
        identity = ApplicationIdentity(
            app_name="blender",
            executable_name="blender.exe",
        )
        state = ApplicationState(
            identity=identity,
            is_running=True,
            is_active=True,
            window_title="Blender [C:\\project.blend]",
        )
        assert state.identity.app_name == "blender"
        assert state.is_running is True
        assert state.is_active is True
        assert state.window_title == "Blender [C:\\project.blend]"


class TestVerificationEngineDeSyntheticized:
    """Test VerificationEngine removes synthetic/hardcoded verification."""

    def test_verify_unobserved_returns_false(self):
        engine = VerificationEngine()

        # Unobserved state (None) returns verified=False and confidence=0.0
        result = engine.verify_action_outcome(
            action_id="act_test_1",
            expected_state="Save document",
            observed_state=None,
        )
        assert result.verified is False
        assert result.confidence == 0.0
        assert "No observed state" in result.details

    def test_verify_unmatched_state_returns_false(self):
        engine = VerificationEngine()

        # Observed state that does not match expected state
        observed = {"is_running": False, "title": "Untitled"}
        result = engine.verify_action_outcome(
            action_id="act_test_2",
            expected_state="Launch Blender 3D",
            observed_state=observed,
        )
        assert result.verified is False
        assert result.confidence == 0.0

    def test_verify_matched_state_returns_true(self):
        engine = VerificationEngine()

        # Observed state matching expected launch
        observed = {"is_running": True, "title": "Blender"}
        result = engine.verify_action_outcome(
            action_id="act_test_3",
            expected_state="Launch Blender",
            observed_state=observed,
        )
        assert result.verified is True
        assert result.confidence >= 0.85


class TestApplicationAdapters:
    """Test BaseApplicationAdapter and BlenderApplicationAdapter extended contracts."""

    @pytest.mark.anyio
    async def test_base_adapter_unsupported_action_fails_honestly(self):
        class GenericAppAdapter(BaseApplicationAdapter):
            pass

        adapter = GenericAppAdapter("generic_app")
        action = AutomationAction(action_type="unsupported_action_xyz")

        result = await adapter.execute(action)
        assert result.success is False
        assert "not supported" in result.error_message.lower()

        # Verify step on failed action returns verified=False, confidence=0.0
        v_result = await adapter.verify(action, result)
        assert v_result.verified is False
        assert v_result.confidence == 0.0

    @pytest.mark.anyio
    async def test_blender_adapter_rejects_raw_python(self):
        adapter = BlenderApplicationAdapter()
        action = AutomationAction(
            action_type="raw_python",
            value={"script": "import os; os.system('calc')"},
        )

        assert adapter.can_handle_action(action) is False
        result = await adapter.execute(action)
        assert result.success is False
        assert "forbidden" in result.error_message.lower()

    @pytest.mark.anyio
    async def test_blender_adapter_valid_action_contract(self):
        adapter = BlenderApplicationAdapter()
        action = AutomationAction(
            action_type="create_object",
            value={"type": "MESH"},
        )
        assert adapter.can_handle_action(action) is True

        caps = adapter.get_capabilities()
        assert "create_object" in caps


class TestAutomationRouter:
    """Test 5-Tier AutomationRouter selection logic."""

    def test_route_blender_native_api(self):
        registry = ApplicationAdapterRegistry()
        blender_adapter = BlenderApplicationAdapter()
        registry.register(blender_adapter)

        router = AutomationRouter(registry)

        action = AutomationAction(
            action_type="create_object",
            value={"type": "MESH"},
        )
        decision = router.route_action("blender", action)

        assert decision.tier == AutomationTier.TIER_1_NATIVE_API
        assert decision.tier_name == "TIER_1_NATIVE_API"
        assert decision.adapter is not None

    def test_route_unregistered_app_falls_back(self):
        router = AutomationRouter()
        action = AutomationAction(action_type="click", target_label="Save")

        decision = router.select_strategy(action)
        assert decision.tier in (AutomationTier.TIER_3_UI_AUTOMATION, AutomationTier.TIER_5_GENERIC_FALLBACK)


class TestNativeBridgeClient:
    """Test Python NativeBridgeClient IPC client."""

    def test_client_init(self):
        client = NativeBridgeClient(base_url="http://127.0.0.1:3001")
        assert client.base_url == "http://127.0.0.1:3001"

    @patch("urllib.request.urlopen")
    def test_health_check_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = NativeBridgeClient()
        assert client.health_check() is True

    @patch("urllib.request.urlopen")
    def test_execute_native_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"requestId": "req1", "status": "COMPLETED", "success": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = NativeBridgeClient()
        res = client.execute_native("os_control", "get_active_window")
        assert res.get("success") is True or res.get("status") == "COMPLETED"
