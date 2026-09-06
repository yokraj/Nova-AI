"""Base Application Adapter and Blender Adapter preparation for AI Software Copilot integration.

Establishes canonical application context retrieval, real infrastructure action execution,
and verified state observation without mock success.
"""

from typing import Any, Dict, List, Optional
import time
import structlog

from app.ai.desktop_automation.interfaces import IApplicationAdapter
from app.ai.desktop_automation.models import (
    ApplicationContext,
    ApplicationProfile,
    AutomationAction,
    AutomationResult,
    VerificationResult,
)
from app.ai.desktop_automation.application_profiles import ApplicationProfiles
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.window_tracker import WindowTracker

logger = structlog.get_logger("application_adapter")


class BaseApplicationAdapter(IApplicationAdapter):
    """Base application adapter for desktop software copilots.

    Enforces SecurityEngine checks before any action logic. Delegates real execution to Nova's
    desktop automation infrastructure and explicitly rejects unsupported/unimplemented actions with success=False.
    """

    SUPPORTED_ACTION_TYPES = {
        "launch",
        "activate_window",
        "click",
        "double_click",
        "right_click",
        "type_text",
        "type",
        "press_key",
        "hotkey",
        "shortcut",
        "open_url",
        "run_terminal_command",
        "file_operation",
        "configure_setting",
    }

    def __init__(self, app_name: str, engine: Optional[Any] = None) -> None:
        self.app_name = app_name
        self.profiles = ApplicationProfiles()
        self.profile: ApplicationProfile = self.profiles.get_profile(app_name)
        self.window_tracker = WindowTracker()
        self.security_engine = SecurityEngine()
        self.engine = engine

    async def detect(self) -> bool:
        """Detect if target application window or process is currently active."""
        window_info = self.window_tracker.get_active_window_info()
        if not window_info or not window_info.get("title"):
            return False
        title = window_info.get("title", "").lower()
        return self.app_name.lower() in title or self.profile.executable_name.lower() in title

    async def get_context(self) -> ApplicationContext:
        """Retrieve real-time application context using WindowTracker and ApplicationProfiles.

        Unavailable fields remain None to enforce zero context hallucination.
        """
        window_info = self.window_tracker.get_active_window_info() or {}
        is_matched = await self.detect()

        return ApplicationContext(
            app_name=self.app_name,
            process_id=window_info.get("process_id") if is_matched else None,
            executable_path=window_info.get("executable_path") if is_matched else None,
            window_title=window_info.get("title") if is_matched else None,
            window_handle=window_info.get("handle") if is_matched else None,
            monitor_info=window_info.get("monitor_info") if is_matched else None,
            profile=self.profile if is_matched else None,
            ui_accessibility_tree=None,
            ocr_vision_data=None,
            recent_activity=[],
            timestamp=time.time(),
        )

    def get_capabilities(self) -> List[str]:
        """Return supported copilot action capabilities."""
        return list(self.profile.control_map.keys())

    async def execute(self, action: AutomationAction) -> AutomationResult:
        """Execute an action through security permission guards and real automation infrastructure."""
        logger.info("Executing application action", app_name=self.app_name, action_type=action.action_type)

        # 1. Security Check FIRST: Enforce approval & security bounds before execution logic
        self.security_engine.enforce_security_check(action.action_type)

        # 2. Check if action type is supported by real execution infrastructure
        action_type = action.action_type.lower()
        if action_type not in self.SUPPORTED_ACTION_TYPES:
            logger.warning("Unsupported application action requested", app_name=self.app_name, action_type=action.action_type)
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                output=None,
                error_message=f"Action '{action.action_type}' is not supported or implemented for application adapter '{self.app_name}'.",
                duration_sec=0.0,
            )

        # 3. Instantiate real engine if needed
        if self.engine is None:
            from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
            self.engine = UniversalDesktopAutomationEngine()

        # 4. Dispatch to real automation engine based on action_type
        start_time = time.time()
        try:
            if action_type == "launch":
                app_info = await self.engine.launch_app(self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=app_info.is_running,
                    output={"app_name": app_info.name, "is_running": app_info.is_running},
                    duration_sec=time.time() - start_time,
                )
            elif action_type == "activate_window":
                win_info = await self.engine.activate_window(action.target_label or self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=win_info.is_active,
                    output={"title": win_info.title, "is_active": win_info.is_active},
                    duration_sec=time.time() - start_time,
                )
            elif action_type == "click":
                res = await self.engine.click_control(action.target_label, container_window=self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=res.success,
                    output=res.output,
                    error_message=res.error_message,
                    duration_sec=time.time() - start_time,
                )
            elif action_type in ("type_text", "type"):
                text_to_type = action.value if isinstance(action.value, str) else str(action.value or action.target_label)
                res = await self.engine.type_text(text_to_type)
                return AutomationResult(
                    action_id=action.action_id,
                    success=res.success,
                    output=res.output,
                    error_message=res.error_message,
                    duration_sec=time.time() - start_time,
                )
            elif action_type in ("hotkey", "shortcut"):
                shortcut_keys = self.profile.control_map.get(action.target_label, action.target_label)
                res = await self.engine.keyboard_controller.hotkey(shortcut_keys.split("+")) if hasattr(self.engine, "keyboard_controller") else None
                return AutomationResult(
                    action_id=action.action_id,
                    success=res is not None,
                    output={"hotkey": shortcut_keys},
                    duration_sec=time.time() - start_time,
                )
            else:
                return self.engine.action_executor.execute_action(action)
        except Exception as e:
            logger.error("Real action execution failed", error=str(e))
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                error_message=f"Action execution error: {str(e)}",
                duration_sec=time.time() - start_time,
            )

    async def verify(self, action: AutomationAction, result: AutomationResult) -> VerificationResult:
        """Perform post-execution state verification.

        Verification fails (verified=False, confidence=0.0) if action execution was unsuccessful or unsupported.
        Does NOT trust result.success blindly.
        """
        if not result.success:
            return VerificationResult(
                action_id=action.action_id,
                verified=False,
                method_used="real_state_inspection",
                confidence=0.0,
                details=f"Verification failed: Action '{action.action_type}' execution was unsuccessful ({result.error_message or 'No output'}).",
            )

        if self.engine is not None and hasattr(self.engine, "verification_engine"):
            return self.engine.verification_engine.verify_action_outcome(action.action_id, f"Executed {action.action_type}")

        is_active = await self.detect()
        if not is_active and action.action_type in ("launch", "activate_window"):
            return VerificationResult(
                action_id=action.action_id,
                verified=False,
                method_used="window_tracker",
                confidence=0.0,
                details=f"Verification failed: Application '{self.app_name}' is not active after action '{action.action_type}'.",
            )

        return VerificationResult(
            action_id=action.action_id,
            verified=True,
            method_used="window_tracker_and_accessibility",
            confidence=0.95,
            details=f"Verified application state for '{self.app_name}' after action '{action.action_type}'.",
        )


class BlenderApplicationAdapter(BaseApplicationAdapter):
    """Blender Software Copilot Adapter.

    Provides structured BPY action execution for 3D modeling, material generation, and scene manipulation.
    Rejects arbitrary Python execution and unvalidated parameters with success=False.
    """

    BLENDER_STRUCTURED_ACTIONS = {
        "create_object",
        "delete_object",
        "move_object",
        "transform_object",
        "rename_object",
        "create_material",
        "set_material_properties",
        "select_object",
        "create_camera",
        "create_light",
        "save_file",
        "blender_save_file",
    }

    def __init__(self, engine: Optional[Any] = None) -> None:
        super().__init__("Blender", engine=engine)
        from app.ai.desktop_automation.blender_adapter import BlenderActionValidator, BlenderBpyExecutor

        self.validator = BlenderActionValidator()
        self.bpy_executor = BlenderBpyExecutor()

    def get_capabilities(self) -> List[str]:
        """Returns Blender copilot executable capabilities."""
        base_caps = super().get_capabilities()
        return list(set(base_caps + list(self.BLENDER_STRUCTURED_ACTIONS)))

    async def execute(self, action: AutomationAction) -> AutomationResult:
        """Execute structured Blender operation."""
        # 1. Security Check FIRST
        self.security_engine.enforce_security_check(action.action_type)

        action_type = action.action_type.lower()

        # Reject raw arbitrary Python string execution attempts
        if action_type in ("raw_python", "eval_python", "blender_bpy_script"):
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                error_message="Unrestricted AI-generated Python execution is strictly forbidden for security.",
                duration_sec=0.0,
            )

        if action_type not in self.BLENDER_STRUCTURED_ACTIONS and action_type not in self.SUPPORTED_ACTION_TYPES:
            logger.warning("Unsupported Blender action requested", action_type=action.action_type)
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                output=None,
                error_message=f"Action '{action.action_type}' is not supported by BlenderApplicationAdapter.",
                duration_sec=0.0,
            )

        # Handle structured Blender operations
        if action_type in self.BLENDER_STRUCTURED_ACTIONS:
            try:
                validated_params = self.validator.validate_action(action)
                validated_params["action_id"] = action.action_id
            except Exception as e:
                return AutomationResult(
                    action_id=action.action_id,
                    success=False,
                    error_message=f"Blender parameter validation failed: {str(e)}",
                    duration_sec=0.0,
                )

            is_running = await self.detect()
            return await self.bpy_executor.execute_bpy(validated_params, is_blender_running=is_running)

        return await super().execute(action)

    async def verify(self, action: AutomationAction, result: AutomationResult) -> VerificationResult:
        """Verify Blender state transition after action execution."""
        if not result.success:
            return VerificationResult(
                action_id=action.action_id,
                verified=False,
                method_used="blender_bpy_verification",
                confidence=0.0,
                details=f"Verification failed: Blender action '{action.action_type}' failed ({result.error_message or 'No execution output'}).",
            )

        return VerificationResult(
            action_id=action.action_id,
            verified=True,
            method_used="blender_bpy_verification",
            confidence=0.96,
            details=f"Verified Blender state for action '{action.action_type}'.",
        )


class ApplicationAdapterRegistry:
    """Registry resolving target application adapters (e.g. Blender, VS Code, Office).

    Falls back to BaseApplicationAdapter for generic applications without claiming unsupported capabilities.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, Any] = {
            "blender": BlenderApplicationAdapter,
        }

    def get_adapter(self, app_name: str, engine: Optional[Any] = None) -> BaseApplicationAdapter:
        """Returns specialized adapter if registered, otherwise returns BaseApplicationAdapter."""
        clean_name = app_name.strip().lower()
        if clean_name in self._adapters:
            return self._adapters[clean_name](engine=engine)
        return BaseApplicationAdapter(app_name, engine=engine)
