"""Test Suite for Blender Phase 6 — Animation & Rigging.

Covers unit validation, adapter integration, execution protocol failure modes,
physical verification against installed Blender 5.2.0 LTS including animation, keyframing,
armatures, bone hierarchies, pose animation, binding, drivers, NLA, and fresh-process persistence.
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
from app.ai.desktop_automation.blender_executors.animation_executor import (
    BlenderAnimationExecutor,
    SUPPORTED_ANIMATION_ACTIONS,
)
from app.ai.desktop_automation.automation_router import AutomationRouter
from app.ai.desktop_automation.models import AutomationAction

logger = structlog.get_logger("test_blender_phase6")


@pytest.fixture
def blender_path():
    path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    if not os.path.exists(path):
        pytest.skip(f"Blender executable not found at {path}")
    return path


class TestBlenderAnimationValidatorUnit:
    """Unit tests for Phase 6 action validation."""

    def test_all_84_actions_recognized(self):
        assert len(SUPPORTED_ANIMATION_ACTIONS) == 84
        validator = BlenderActionValidator()
        for act in SUPPORTED_ANIMATION_ACTIONS:
            assert act in validator.ANIMATION_ACTIONS

    def test_validate_set_current_frame(self):
        action = AutomationAction(
            action_type="set_current_frame",
            value={"frame": 42}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "set_current_frame"
        assert res["frame"] == 42

    def test_validate_insert_object_keyframe(self):
        action = AutomationAction(
            action_type="insert_object_keyframe",
            value={"name": "Cube", "data_path": "location", "frame": 10, "value": [1.0, 2.0, 3.0]}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "insert_object_keyframe"
        assert res["name"] == "Cube"
        assert res["data_path"] == "location"

    def test_validate_create_armature(self):
        action = AutomationAction(
            action_type="create_armature",
            value={"name": "HeroRig", "location": [0.0, 0.0, 0.0]}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_armature"
        assert res["name"] == "HeroRig"

    def test_validate_create_bone(self):
        action = AutomationAction(
            action_type="create_bone",
            value={"armature_name": "HeroRig", "bone_name": "Head", "head": [0, 0, 1], "tail": [0, 0, 2]}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_bone"
        assert res["armature_name"] == "HeroRig"
        assert res["bone_name"] == "Head"

    def test_reject_invalid_interpolation(self):
        action = AutomationAction(
            action_type="set_keyframe_interpolation",
            value={"name": "Cube", "interpolation": "MAGIC_SMOOTH"}
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "invalid interpolation" in str(excinfo.value).lower()

    def test_reject_invalid_easing(self):
        action = AutomationAction(
            action_type="set_keyframe_easing",
            value={"name": "Cube", "easing": "SUPER_EASE"}
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "invalid easing" in str(excinfo.value).lower()

    def test_reject_invalid_constraint_type(self):
        action = AutomationAction(
            action_type="add_animation_constraint",
            value={"name": "Cube", "constraint_type": "UNSUPPORTED_PHYSICS"}
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "invalid constraint_type" in str(excinfo.value).lower()

    def test_reject_forbidden_python_keys(self):
        action = AutomationAction(
            action_type="insert_object_keyframe",
            value={"name": "Cube", "raw_python": "import os; os.system('calc')"}
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "strictly forbidden" in str(excinfo.value).lower()


class TestBlenderAdapterIntegrationPhase6:
    """Integration tests for Phase 6 registrations in adapter and router."""

    def test_all_243_actions_in_adapter_capabilities(self):
        adapter = BlenderApplicationAdapter()
        assert len(adapter.BLENDER_STRUCTURED_ACTIONS) >= 243
        caps = adapter.get_capabilities()
        for act in SUPPORTED_ANIMATION_ACTIONS:
            assert act in caps


    def test_router_integration_phase6(self):
        for act in SUPPORTED_ANIMATION_ACTIONS:
            assert act in AutomationRouter.TIER_1_ACTIONS

    @pytest.mark.asyncio
    async def test_security_blocks_raw_python(self):
        adapter = BlenderApplicationAdapter()
        action = AutomationAction(
            action_type="insert_object_keyframe",
            value={"name": "Cube", "exec": "import os; os.system('echo HACKED')"}
        )
        res = await adapter.execute(action)
        assert res.success is False
        assert "forbidden" in res.error_message.lower() or "error" in res.error_message.lower()


class TestBlenderExecutionProtocolFailureModesPhase6:
    """Tests failure handling and syntax validation of Phase 6 BPY templates."""

    def test_animation_executor_templates_syntax(self):
        executor = BlenderAnimationExecutor()
        for action_type in SUPPORTED_ANIMATION_ACTIONS:
            params = {
                "action_type": action_type,
                "name": "TestObj",
                "object_name": "TestObj",
                "armature_name": "TestArm",
                "bone_name": "TestBone",
                "action_name": "TestAction",
                "new_name": "NewName",
                "parent_bone": "RootBone",
                "track_name": "TestTrack",
                "strip_name": "TestStrip",
                "target_object": "TargetObj",
                "constraint_name": "TestCon",
                "frame": 10,
                "start_frame": 1,
                "end_frame": 100,
                "data_path": "location",
                "value": [1.0, 2.0, 3.0],
                "location": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
                "head": [0.0, 0.0, 0.0],
                "tail": [0.0, 0.0, 1.0],
                "interpolation": "BEZIER",
                "easing": "AUTO",
                "handle_type": "AUTO",
                "extrapolation": "CONSTANT",
                "constraint_type": "COPY_LOCATION",
            }
            script = executor.build_script(action_type, params)
            assert "NOVA_ACTION_START" in script
            assert ("NOVA_ACTION_SUCCESS" in script or "NOVA_ACTION_ERROR" in script)
            compile(script, "<string>", "exec")


class TestBlenderPhysicalAnimationRiggingVerification:
    """Physical Blender execution tests verifying animation, keyframes, armatures, bones, pose, drivers, NLA, and persistence."""

    @pytest.mark.asyncio
    async def test_physical_animation_rigging_workflow(self, blender_path):
        executor = BlenderBpyExecutor()
        blend_file = os.path.join(tempfile.gettempdir(), "test_phase6_anim.blend")
        if os.path.exists(blend_file):
            os.remove(blend_file)

        # 0. Initial Save
        res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file}, is_blender_running=False)
        assert res0.success is True

        # 1. Timeline Setup
        res = await executor.execute_bpy({"action_type": "set_frame_range", "start_frame": 1, "end_frame": 120}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_current_frame", "frame": 1}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 2. Armature & Bone Creation
        res = await executor.execute_bpy({"action_type": "create_armature", "name": "CharacterRig", "location": [0.0, 0.0, 0.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "create_bone", "armature_name": "CharacterRig", "bone_name": "RootBone", "head": [0, 0, 0], "tail": [0, 0, 1]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "create_bone", "armature_name": "CharacterRig", "bone_name": "SpineBone", "head": [0, 0, 1], "tail": [0, 0, 2], "parent_bone": "RootBone"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 3. Mesh Object & Armature Binding
        res = await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "cube", "name": "CharacterMesh", "object_name": "CharacterMesh"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "add_armature_modifier", "object_name": "CharacterMesh", "armature_name": "CharacterRig", "modifier_name": "ArmatureMod"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "validate_armature_binding", "object_name": "CharacterMesh", "armature_name": "CharacterRig"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 4. Pose Mode Animation
        res = await executor.execute_bpy({"action_type": "set_pose_bone_location", "armature_name": "CharacterRig", "bone_name": "SpineBone", "location": [0.0, 0.5, 0.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "insert_pose_bone_keyframe", "armature_name": "CharacterRig", "bone_name": "SpineBone", "data_path": "location", "frame": 1}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 5. Object Keyframing & Actions
        res = await executor.execute_bpy({"action_type": "insert_object_keyframe", "name": "CharacterMesh", "data_path": "location", "frame": 1, "value": [0.0, 0.0, 0.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "insert_object_keyframe", "name": "CharacterMesh", "data_path": "location", "frame": 30, "value": [5.0, 0.0, 0.0]}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "set_keyframe_interpolation", "name": "CharacterMesh", "interpolation": "BEZIER", "data_path": "location"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 6. Drivers & NLA
        res = await executor.execute_bpy({"action_type": "create_driver", "name": "CharacterMesh", "data_path": "rotation_euler", "index": 2, "target_object": "CharacterRig", "target_data_path": "location", "target_index": 0}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "validate_driver", "name": "CharacterMesh", "data_path": "rotation_euler"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "create_action", "action_name": "WalkCycle"}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        res = await executor.execute_bpy({"action_type": "add_nla_strip", "name": "CharacterMesh", "track_name": "LocomotionTrack", "action_name": "WalkCycle", "start_frame": 1}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True

        # 7. Save file
        res = await executor.execute_bpy({"action_type": "blender_save_file", "filepath": blend_file}, is_blender_running=False, blend_filepath=blend_file)
        assert res.success is True
        assert os.path.exists(blend_file)

        # 8. Reopen in completely FRESH Blender process and verify persistence
        res_frame = await executor.execute_bpy(
            {"action_type": "get_frame_range"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_frame.success is True
        assert "1_120" in res_frame.output.get("stdout", "")

        res_arm = await executor.execute_bpy(
            {"action_type": "get_armature_state", "name": "CharacterRig"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_arm.success is True
        arm_out = res_arm.output.get("stdout", "")
        assert "RootBone" in arm_out
        assert "SpineBone" in arm_out

        res_pose = await executor.execute_bpy(
            {"action_type": "get_pose_bone_state", "armature_name": "CharacterRig", "bone_name": "SpineBone"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_pose.success is True
        assert "SpineBone" in res_pose.output.get("stdout", "")

        res_nla = await executor.execute_bpy(
            {"action_type": "get_nla_tracks", "name": "CharacterMesh"},
            is_blender_running=False,
            blend_filepath=blend_file,
        )
        assert res_nla.success is True
        assert "LocomotionTrack" in res_nla.output.get("stdout", "")


class TestBlenderAnimationFailureModes:
    """Failure mode tests for invalid animation/rigging references."""

    @pytest.mark.asyncio
    async def test_nonexistent_object_keyframe_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "insert_object_keyframe", "name": "GhostObject", "data_path": "location", "frame": 1}, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_armature_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "create_bone", "armature_name": "GhostArm", "bone_name": "Bone1"}, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_action_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "get_action", "action_name": "GhostAction"}, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()
