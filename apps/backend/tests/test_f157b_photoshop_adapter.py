"""Tests for Nova-AI F1.57-B Adobe Photoshop Copilot Adapter.

Covers:
- PhotoshopActionValidator action validation, schema checks, and path safety
- PhotoshopApplicationAdapter identity detection & state observation
- Security gate enforcement (blocking arbitrary script execution raw_python/jsx/extendscript)
- 5-Tier AutomationRouter routing for Photoshop actions
- ApplicationAdapterRegistry integration & dynamic adapter selection
- Honest unobserved / unavailable handling (success=False, verified=False, confidence=0.0)
- Mocked COM execution and empirical verification
"""

import pytest
from unittest.mock import MagicMock, patch

from app.ai.desktop_automation.models import (
    ApplicationContext,
    ApplicationIdentity,
    ApplicationState,
    AutomationAction,
    AutomationPriority,
    AutomationResult,
)
from app.ai.desktop_automation.photoshop_adapter import (
    PhotoshopActionValidator,
    PhotoshopActionValidationError,
    PhotoshopComExecutor,
    PhotoshopApplicationAdapter,
)
from app.ai.desktop_automation.application_adapter import (
    ApplicationAdapterRegistry,
)
from app.ai.desktop_automation.automation_router import (
    AutomationRouter,
    AutomationTier,
)


class TestPhotoshopActionValidator:
    """Test Photoshop action parameter validation and security checks."""

    def test_supported_actions_list(self):
        actions = PhotoshopActionValidator.SUPPORTED_ACTIONS
        assert len(actions) == 11
        assert "create_document" in actions
        assert "open_document" in actions
        assert "save_document" in actions
        assert "save_as" in actions
        assert "close_document" in actions
        assert "create_layer" in actions
        assert "delete_layer" in actions
        assert "rename_layer" in actions
        assert "select_layer" in actions
        assert "duplicate_layer" in actions
        assert "export_document" in actions

    def test_validate_create_document_valid(self):
        action = AutomationAction(
            action_id="act_1",
            action_type="create_document",
            target="photoshop",
            value={"width": 1920, "height": 1080, "resolution": 72, "name": "Untitled-1"},
        )
        params = PhotoshopActionValidator.validate_action(action)
        assert params["width"] == 1920
        assert params["height"] == 1080
        assert params["name"] == "Untitled-1"

    def test_validate_open_document_valid(self):
        action = AutomationAction(
            action_id="act_2",
            action_type="open_document",
            target="photoshop",
            value={"file_path": "C:\\images\\photo.psd"},
        )
        params = PhotoshopActionValidator.validate_action(action)
        assert params["file_path"] == "C:\\images\\photo.psd"

    def test_validate_open_document_missing_path(self):
        action = AutomationAction(
            action_id="act_3",
            action_type="open_document",
            target="photoshop",
            value={},
        )
        with pytest.raises(PhotoshopActionValidationError) as exc_info:
            PhotoshopActionValidator.validate_action(action)
        assert "requires a valid 'file_path'" in str(exc_info.value)

    def test_validate_path_safety_violation(self):
        action = AutomationAction(
            action_id="act_4",
            action_type="open_document",
            target="photoshop",
            value={"file_path": "C:\\images\\photo.psd; rm -rf /"},
        )
        with pytest.raises(PhotoshopActionValidationError) as exc_info:
            PhotoshopActionValidator.validate_action(action)
        assert "prohibited character" in str(exc_info.value)

    def test_validate_unsupported_action(self):
        action = AutomationAction(
            action_id="act_unsupported",
            action_type="unsupported_ps_action",
            target="photoshop",
            value={},
        )
        with pytest.raises(PhotoshopActionValidationError) as exc_info:
            PhotoshopActionValidator.validate_action(action)
        assert "not a supported structured Photoshop action" in str(exc_info.value)


class TestPhotoshopApplicationAdapter:
    """Test Photoshop application adapter capabilities, observation, security, and execution."""

    def setup_method(self):
        self.adapter = PhotoshopApplicationAdapter()

    def test_can_handle_action(self):
        valid_action = AutomationAction(action_id="1", action_type="create_document", target="photoshop")
        assert self.adapter.can_handle_action(valid_action) is True

        forbidden_action = AutomationAction(action_id="2", action_type="raw_python", target="photoshop")
        assert self.adapter.can_handle_action(forbidden_action) is False

        unsupported_action = AutomationAction(action_id="3", action_type="unknown_action", target="photoshop")
        assert self.adapter.can_handle_action(unsupported_action) is False

    def test_get_identity_unobserved(self):
        with patch.object(self.adapter.window_tracker, "get_active_window_info", return_value={}):
            identity = self.adapter.get_identity()
            assert identity is None

    @pytest.mark.asyncio
    async def test_observe_unobserved(self):
        with patch.object(self.adapter.window_tracker, "get_active_window_info", return_value={}):
            state = await self.adapter.observe()
            assert isinstance(state, ApplicationState)
            assert state.is_running is False
            assert state.is_active is False

    @pytest.mark.asyncio
    async def test_execute_unobserved_returns_honest_failure(self):
        action = AutomationAction(
            action_id="act_create",
            action_type="create_document",
            target="photoshop",
            value={"width": 800, "height": 600},
        )
        result = await self.adapter.execute(action)
        assert isinstance(result, AutomationResult)
        assert result.success is False
        assert "Photoshop COM automation interface is unavailable" in result.error_message

        verification = await self.adapter.verify(action, result)
        assert verification.verified is False
        assert verification.confidence == 0.0

    @pytest.mark.asyncio
    async def test_execute_arbitrary_script_blocked_by_security(self):
        action = AutomationAction(
            action_id="act_script",
            action_type="raw_python",
            target="photoshop",
            value={"code": "print('evil')"},
        )
        result = await self.adapter.execute(action)
        assert result.success is False
        assert "forbidden" in result.error_message.lower() or "not supported" in result.error_message.lower()

        verification = await self.adapter.verify(action, result)
        assert verification.verified is False
        assert verification.confidence == 0.0

    @pytest.mark.asyncio
    async def test_mocked_com_execution_create_document(self):
        mock_com = MagicMock()
        mock_com.execute_action.return_value = {
            "success": True,
            "document_name": "TestDoc",
            "width": 1000,
            "height": 1000,
        }
        self.adapter.com_executor = mock_com

        with patch.object(self.adapter, "observe") as mock_observe:
            mock_observe.return_value = ApplicationState(
                identity=ApplicationIdentity(
                    app_name="Adobe Photoshop",
                    bundle_id="Adobe.Photoshop",
                    executable_name="photoshop.exe",
                    process_id=1234,
                ),
                is_running=True,
                is_active=True,
            )
            action = AutomationAction(
                action_id="act_com",
                action_type="create_document",
                target="photoshop",
                value={"width": 1000, "height": 1000, "name": "TestDoc"},
            )
            result = await self.adapter.execute(action)
            assert result.success is True
            mock_com.execute_action.assert_called_once()

    def test_registry_integration(self):
        registry = ApplicationAdapterRegistry()
        registry.register_adapter("photoshop", lambda engine=None: self.adapter)

        retrieved = registry.get_adapter("photoshop")
        assert retrieved is self.adapter

    def test_router_integration(self):
        registry = ApplicationAdapterRegistry()
        registry.register_adapter("photoshop", lambda engine=None: self.adapter)
        router = AutomationRouter(registry)

        action = AutomationAction(
            action_id="act_route",
            action_type="create_document",
            target="photoshop",
            value={"width": 800, "height": 600},
        )

        decision = router.route_action("photoshop", action)
        assert decision.tier in (AutomationTier.TIER_1_NATIVE_API, AutomationTier.TIER_2_IPC_COM_CLI)
        assert decision.adapter is self.adapter
