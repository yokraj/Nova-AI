"""Test Suite for Blender Phase 5 — Camera & Lighting.

Covers unit validation, adapter integration, execution protocol failure modes,
physical verification against installed Blender 5.2.0 LTS including three-point-light workflow
and fresh-process persistence.
"""

import pytest
import os
import tempfile
import structlog

from app.ai.desktop_automation.blender_adapter import (
    BlenderActionValidator,
    BlenderActionValidationError,
    BlenderBpyExecutor,
)
from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter
from app.ai.desktop_automation.blender_executors.camera_lighting_executor import (
    BlenderCameraLightingExecutor,
    SUPPORTED_CAMERA_LIGHTING_ACTIONS,
)
from app.ai.desktop_automation.automation_router import AutomationRouter, AutomationTier
from app.ai.desktop_automation.models import AutomationAction

logger = structlog.get_logger("test_blender_phase5")


@pytest.fixture
def blender_path():
    path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    if not os.path.exists(path):
        pytest.skip(f"Blender executable not found at {path}")
    return path


class TestBlenderCameraLightingValidatorUnit:
    """Unit tests for Phase 5 action validation."""

    def test_all_48_actions_recognized(self):
        assert len(SUPPORTED_CAMERA_LIGHTING_ACTIONS) == 48
        validator = BlenderActionValidator()
        for act in SUPPORTED_CAMERA_LIGHTING_ACTIONS:
            assert act in validator.CAMERA_LIGHTING_ACTIONS

    def test_validate_create_camera(self):
        action = AutomationAction(
            action_type="create_camera",
            value={"name": "StudioCam", "lens": 85.0, "clip_start": 0.2, "clip_end": 500.0, "camera_type": "PERSP"}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_camera"
        assert res["camera_name"] == "StudioCam"
        assert res["lens"] == 85.0
        assert res["camera_type"] == "PERSP"

    def test_validate_create_light(self):
        action = AutomationAction(
            action_type="create_light",
            value={"name": "KeyLight", "light_type": "SPOT", "energy": 1500.0, "color": [1.0, 0.9, 0.8]}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_light"
        assert res["light_name"] == "KeyLight"
        assert res["light_type"] == "SPOT"
        assert res["energy"] == 1500.0
        assert list(res["color"]) == [1.0, 0.9, 0.8]

    def test_validate_kelvin_temperature(self):
        rgb = BlenderCameraLightingExecutor.kelvin_to_rgb(5500.0)
        assert len(rgb) == 3
        assert 0.0 <= rgb[0] <= 1.0
        assert 0.0 <= rgb[1] <= 1.0
        assert 0.0 <= rgb[2] <= 1.0

        action = AutomationAction(
            action_type="set_light_temperature",
            value={"light_name": "WarmSun", "temperature": 3200.0}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["temperature"] == 3200.0

    def test_reject_unsupported_camera_type(self):
        action = AutomationAction(
            action_type="set_camera_type",
            value={"camera_name": "MainCam", "camera_type": "FISHEYE_INVALID"}
        )
        with pytest.raises(BlenderActionValidationError) as exc_info:
            BlenderActionValidator.validate_action(action)
        assert "Invalid camera_type" in str(exc_info.value)

    def test_reject_unsupported_light_type(self):
        action = AutomationAction(
            action_type="set_light_type",
            value={"light_name": "Lamp1", "light_type": "LASER_INVALID"}
        )
        with pytest.raises(BlenderActionValidationError) as exc_info:
            BlenderActionValidator.validate_action(action)
        assert "Invalid light_type" in str(exc_info.value)

    def test_reject_invalid_lens_length(self):
        action = AutomationAction(
            action_type="set_camera_lens",
            value={"camera_name": "MainCam", "lens": -50.0}
        )
        with pytest.raises(BlenderActionValidationError) as exc_info:
            BlenderActionValidator.validate_action(action)
        assert "Lens focal length must be > 0" in str(exc_info.value)

    def test_reject_negative_energy(self):
        action = AutomationAction(
            action_type="set_light_energy",
            value={"light_name": "Spot1", "energy": -100.0}
        )
        with pytest.raises(BlenderActionValidationError) as exc_info:
            BlenderActionValidator.validate_action(action)
        assert "Light energy must be >= 0" in str(exc_info.value)

    def test_reject_forbidden_python_keys(self):
        action = AutomationAction(
            action_type="create_camera",
            value={"name": "Cam1", "raw_python": "import os; os.system('calc')"}
        )
        with pytest.raises(BlenderActionValidationError) as exc_info:
            BlenderActionValidator.validate_action(action)
        assert "strictly forbidden" in str(exc_info.value)


class TestBlenderAdapterIntegrationPhase5:
    """Integration tests for adapter registration, capability discovery, and router tiering."""

    def test_all_162_actions_in_capabilities(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        assert len(caps) >= 162
        for act in SUPPORTED_CAMERA_LIGHTING_ACTIONS:
            assert act in caps

    def test_router_integration_phase5(self):
        router = AutomationRouter()
        for act in ("create_camera", "create_light", "track_camera_to_object", "set_light_temperature", "validate_lighting"):
            action = AutomationAction(action_type=act, value={"name": "TestObj"})
            decision = router.select_strategy(action, adapter=BlenderApplicationAdapter())
            assert decision.tier == AutomationTier.TIER_1_NATIVE_API

    @pytest.mark.asyncio
    async def test_security_blocks_raw_python(self):
        adapter = BlenderApplicationAdapter()
        action = AutomationAction(action_type="create_camera", value={"raw_python": "import sys"})
        res = await adapter.execute(action)
        assert res.success is False
        assert "forbidden" in res.error_message.lower() or "error" in res.error_message.lower()


class TestBlenderExecutionProtocolFailureModesPhase5:
    """Tests failure handling and syntax validation of Phase 5 BPY templates."""

    def test_camera_lighting_executor_templates_syntax(self):
        executor = BlenderCameraLightingExecutor()
        for action_type in SUPPORTED_CAMERA_LIGHTING_ACTIONS:
            params = {
                "action_type": action_type,
                "name": "TestCam",
                "camera_name": "TestCam",
                "light_name": "TestLight",
                "new_name": "NewName",
                "target_object": "Cube",
                "lens": 50.0,
                "energy": 500.0,
                "color": [1.0, 1.0, 1.0],
                "temperature": 5500.0,
                "spot_size": 45.0,
                "spot_blend": 0.5,
                "location": [0.0, 0.0, 5.0],
                "rotation": [0.0, 0.0, 0.0],
                "delta": [1.0, 1.0, 1.0],
            }
            script = executor.build_script(action_type, params)
            assert "NOVA_ACTION_START" in script
            assert ("NOVA_ACTION_SUCCESS" in script or "NOVA_ACTION_ERROR" in script)
            compile(script, "<string>", "exec")


class TestBlenderPhysicalCameraLightingVerification:
    """Physical Blender execution tests verifying cameras, lights, optics, targeting, three-point lighting, and persistence."""

    @pytest.mark.asyncio
    async def test_physical_camera_lighting_three_point_workflow(self, blender_path):
        executor = BlenderBpyExecutor()
        blend_file = os.path.join(tempfile.gettempdir(), "test_phase5_lighting.blend")
        if os.path.exists(blend_file):
            os.remove(blend_file)

        # 0. Initial Save
        res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file}, is_blender_running=False)
        assert res0.success is True

        # 1. Create subject object (Cube)
        res = await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "cube", "name": "SubjectCube", "object_name": "SubjectCube"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 2. Create Camera, set location, point at subject, set lens & DOF
        res = await executor.execute_bpy({"action_type": "create_camera", "camera_name": "MainCamera", "location": [0.0, -8.0, 3.0], "lens": 85.0}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "track_camera_to_object", "camera_name": "MainCamera", "target_object": "SubjectCube"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_camera_dof", "camera_name": "MainCamera", "use_dof": True}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_camera_dof_object", "camera_name": "MainCamera", "target_object": "SubjectCube"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_active_camera", "camera_name": "MainCamera"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 3. Create 3-Point Lighting (Key, Fill, Rim)
        res = await executor.execute_bpy({"action_type": "create_light", "light_name": "KeyLight", "light_type": "SPOT", "energy": 2000.0, "location": [4.0, -4.0, 5.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_light_temperature", "light_name": "KeyLight", "temperature": 5500.0}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "point_light_at", "light_name": "KeyLight", "target_object": "SubjectCube"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "create_light", "light_name": "FillLight", "light_type": "AREA", "energy": 800.0, "location": [-4.0, -4.0, 3.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_light_color", "light_name": "FillLight", "color": [0.8, 0.9, 1.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "create_light", "light_name": "RimLight", "light_type": "SUN", "energy": 5.0, "location": [0.0, 5.0, 6.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 4. Validate Camera and Lighting State
        res = await executor.execute_bpy({"action_type": "validate_camera", "camera_name": "MainCamera"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "validate_lighting"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 5. Final Save to .blend file
        res = await executor.execute_bpy({"action_type": "blender_save_file", "filepath": blend_file}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True
        assert os.path.exists(blend_file)

        # 6. Reopen in completely FRESH Blender process and verify persistence
        res_cam = await executor.execute_bpy(
            {"action_type": "get_camera_state", "camera_name": "MainCamera"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_cam.success is True
        cam_stdout = res_cam.output.get("stdout", "")
        assert "MainCamera" in cam_stdout
        assert "lens=85.0" in cam_stdout
        assert "dof=True" in cam_stdout
        assert "focus_obj=SubjectCube" in cam_stdout

        res_light = await executor.execute_bpy(
            {"action_type": "get_light_state", "light_name": "KeyLight"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_light.success is True
        light_stdout = res_light.output.get("stdout", "")
        assert "KeyLight" in light_stdout
        assert "type=SPOT" in light_stdout
        assert "energy=2000.0" in light_stdout

        res_lighting = await executor.execute_bpy(
            {"action_type": "validate_lighting"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_lighting.success is True
        lighting_stdout = res_lighting.output.get("stdout", "")
        assert "count=4" in lighting_stdout


class TestBlenderCameraLightingFailureModes:
    """Failure mode tests for invalid camera/lighting references and exception handling."""

    @pytest.mark.asyncio
    async def test_nonexistent_camera_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "get_camera_state", "camera_name": "GhostCam"}, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_light_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "get_light_state", "light_name": "GhostLight"}, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()
