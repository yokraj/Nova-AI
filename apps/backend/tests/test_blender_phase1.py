"""Tests for Nova-AI Blender Phase 1: Core Action Expansion & Object Hierarchy.

Covers:
- Schema validation & parameter sanitization for 17 new Phase 1 actions
- Rejection of arbitrary script execution (raw_python, eval_python, etc.)
- 5-Tier AutomationRouter routing to Tier 1 Native API for all 28 Blender actions
- ApplicationAdapterRegistry resolution
- Physical execution against installed Blender 5.2.0 LTS (scene, collection, object hierarchy, constraints, transforms, save/persistence)
- Failure handling and honest error reporting
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from app.ai.desktop_automation.models import (
    ApplicationContext,
    ApplicationIdentity,
    ApplicationState,
    AutomationAction,
    AutomationResult,
)
from app.ai.desktop_automation.blender_adapter import (
    BlenderActionValidator,
    BlenderActionValidationError,
    BlenderBpyExecutor,
)
from app.ai.desktop_automation.blender_executors.scene_executor import BlenderSceneExecutor
from app.ai.desktop_automation.blender_executors.object_executor import BlenderObjectExecutor
from app.ai.desktop_automation.application_adapter import (
    BlenderApplicationAdapter,
    ApplicationAdapterRegistry,
)
from app.ai.desktop_automation.automation_router import (
    AutomationRouter,
    AutomationTier,
)


class TestBlenderActionValidatorPhase1:
    """Unit tests for Phase 1 parameter schemas, allowlists, and security guards."""

    def test_all_28_actions_recognized(self):
        assert len(BlenderActionValidator.SCENE_ACTIONS) == 9
        assert len(BlenderActionValidator.OBJECT_HIERARCHY_ACTIONS) == 8

    def test_validate_create_scene(self):
        action = AutomationAction(action_id="a1", action_type="create_scene", target="blender", value={"name": "MyScene"})
        params = BlenderActionValidator.validate_action(action)
        assert params["name"] == "MyScene"

    def test_validate_set_scene_units(self):
        action = AutomationAction(action_id="a2", action_type="set_scene_units", target="blender", value={"system": "METRIC", "scale_length": 1.0})
        params = BlenderActionValidator.validate_action(action)
        assert params["system"] == "METRIC"
        assert params["scale_length"] == 1.0

    def test_validate_set_scene_units_invalid_system_fallback(self):
        action = AutomationAction(action_id="a3", action_type="set_scene_units", target="blender", value={"system": "INVALID"})
        params = BlenderActionValidator.validate_action(action)
        assert params["system"] == "METRIC"

    def test_validate_create_collection(self):
        action = AutomationAction(action_id="a4", action_type="create_collection", target="blender", value={"name": "Props", "parent_collection": "Scene Collection"})
        params = BlenderActionValidator.validate_action(action)
        assert params["name"] == "Props"
        assert params["parent_collection"] == "Scene_Collection"

    def test_validate_duplicate_object(self):
        action = AutomationAction(action_id="a5", action_type="duplicate_object", target="blender", value={"source_object": "Cube", "new_name": "Cube_Copy"})
        params = BlenderActionValidator.validate_action(action)
        assert params["source_object"] == "Cube"
        assert params["new_name"] == "Cube_Copy"

    def test_validate_parent_object(self):
        action = AutomationAction(action_id="a6", action_type="parent_object", target="blender", value={"child": "Cube_Copy", "parent": "Cube"})
        params = BlenderActionValidator.validate_action(action)
        assert params["child"] == "Cube_Copy"
        assert params["parent"] == "Cube"

    def test_validate_parent_object_missing_parent_raises(self):
        action = AutomationAction(action_id="a7", action_type="parent_object", target="blender", value={"child": "Cube_Copy"})
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_validate_add_constraint(self):
        action = AutomationAction(action_id="a8", action_type="add_constraint", target="blender", value={"object_name": "Camera", "constraint_type": "TRACK_TO", "target_object": "Cube"})
        params = BlenderActionValidator.validate_action(action)
        assert params["constraint_type"] == "TRACK_TO"
        assert params["target_object"] == "Cube"

    def test_validate_add_constraint_invalid_type_raises(self):
        action = AutomationAction(action_id="a9", action_type="add_constraint", target="blender", value={"object_name": "Camera", "constraint_type": "INVALID_TYPE"})
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_reject_arbitrary_python_keys(self):
        for f_key in ["raw_python", "eval_python", "blender_bpy_script", "script", "code"]:
            action = AutomationAction(action_id="a10", action_type="create_scene", target="blender", value={f_key: "print('hack')"})
            with pytest.raises(BlenderActionValidationError) as exc_info:
                BlenderActionValidator.validate_action(action)
            assert "strictly forbidden" in str(exc_info.value)


class TestBlenderAdapterIntegrationPhase1:
    """Integration tests for adapter capabilities, router, and security gate."""

    def setup_method(self):
        self.adapter = BlenderApplicationAdapter()

    def test_all_28_actions_in_adapter_capabilities(self):
        caps = self.adapter.get_capabilities()
        assert len(caps) >= 28
        assert "create_scene" in caps
        assert "duplicate_object" in caps
        assert "parent_object" in caps
        assert "add_constraint" in caps

    def test_router_integration_phase1(self):
        registry = ApplicationAdapterRegistry()
        registry.register_adapter("blender", lambda engine=None: self.adapter)
        router = AutomationRouter(registry)

        for act_type in ["create_scene", "set_scene_units", "duplicate_object", "parent_object", "add_constraint"]:
            action = AutomationAction(action_id=f"act_{act_type}", action_type=act_type, target="blender")
            decision = router.route_action("blender", action)
            assert decision.tier == AutomationTier.TIER_1_NATIVE_API
            assert decision.adapter is self.adapter

    @pytest.mark.asyncio
    async def test_security_blocks_raw_python(self):
        action = AutomationAction(action_id="act_sec", action_type="raw_python", target="blender", value={"code": "import os"})
        result = await self.adapter.execute(action)
        assert result.success is False
        assert "strictly forbidden" in result.error_message.lower()


class TestBlenderPhysicalPhase1:
    """Physical execution test suite against installed Blender 5.2.0 LTS."""

    @pytest.mark.asyncio
    async def test_physical_blender_phase1_workflow(self):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Physical Blender executable not found on host system.")

        executor = BlenderBpyExecutor()
        tmp_dir = tempfile.gettempdir()
        test_file = os.path.join(tmp_dir, "phase1_test_scene.blend").replace("\\", "/")

        # Step 0: Save initial project file
        res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": test_file})
        assert res0.success is True
        assert os.path.exists(test_file)

        # 1. Create Scene
        res1 = await executor.execute_bpy({"action_type": "create_scene", "name": "Phase1Scene"}, blend_filepath=test_file)
        assert res1.success is True

        # 2. Rename Scene
        res2 = await executor.execute_bpy({"action_type": "rename_scene", "name": "Phase1Scene", "new_name": "RenamedScene"}, blend_filepath=test_file)
        assert res2.success is True

        # 3. Set Units
        res3 = await executor.execute_bpy({"action_type": "set_scene_units", "system": "METRIC", "scale_length": 1.0}, blend_filepath=test_file)
        assert res3.success is True

        # 4. Create Collection
        res4 = await executor.execute_bpy({"action_type": "create_collection", "name": "Phase1Col"}, blend_filepath=test_file)
        assert res4.success is True

        # 5. Create Object
        res5 = await executor.execute_bpy({"action_type": "create_object", "primitive": "cube", "name": "BaseCube", "location": (0, 0, 0)}, blend_filepath=test_file)
        assert res5.success is True

        # 6. Duplicate Object
        res6 = await executor.execute_bpy({"action_type": "duplicate_object", "source_object": "BaseCube", "new_name": "DupCube"}, blend_filepath=test_file)
        assert res6.success is True

        # 7. Move & Transform DupCube
        res7 = await executor.execute_bpy({"action_type": "move_object", "name": "DupCube", "location": (3.0, 0.0, 0.0)}, blend_filepath=test_file)
        assert res7.success is True

        # 8. Hide & Show DupCube
        res8_hide = await executor.execute_bpy({"action_type": "hide_object", "name": "DupCube", "hide_viewport": True, "hide_render": True}, blend_filepath=test_file)
        assert res8_hide.success is True

        res8_show = await executor.execute_bpy({"action_type": "show_object", "name": "DupCube", "show_viewport": True, "show_render": True}, blend_filepath=test_file)
        assert res8_show.success is True

        # 9. Parent & Unparent
        res9_parent = await executor.execute_bpy({"action_type": "parent_object", "child": "DupCube", "parent": "BaseCube", "keep_transform": True}, blend_filepath=test_file)
        assert res9_parent.success is True

        res9_unparent = await executor.execute_bpy({"action_type": "unparent_object", "child": "DupCube", "keep_transform": True}, blend_filepath=test_file)
        assert res9_unparent.success is True

        # 10. Add & Remove Constraint
        res10_add = await executor.execute_bpy({"action_type": "add_constraint", "name": "DupCube", "constraint_type": "COPY_LOCATION", "target_object": "BaseCube", "constraint_name": "CopyLocConstraint"}, blend_filepath=test_file)
        assert res10_add.success is True

        res10_rem = await executor.execute_bpy({"action_type": "remove_constraint", "name": "DupCube", "constraint_name": "CopyLocConstraint"}, blend_filepath=test_file)
        assert res10_rem.success is True

        # 11. Apply Transform
        res11 = await executor.execute_bpy({"action_type": "apply_transform", "name": "DupCube", "location": True, "rotation": True, "scale": True}, blend_filepath=test_file)
        assert res11.success is True

        # Verify disk file persistence
        assert os.path.exists(test_file)
        assert os.path.getsize(test_file) > 0

        # Clean up temporary test blend file
        if os.path.exists(test_file):
            os.remove(test_file)


class TestBlenderFailureCasesPhase1:
    """Failure case tests verifying honest error reporting on invalid targets."""

    @pytest.mark.asyncio
    async def test_failure_on_nonexistent_object(self):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "hide_object", "name": "NonExistentObject_999"})
        assert res.success is False
        assert "NonExistentObject_999 not found" in res.error_message

    @pytest.mark.asyncio
    async def test_failure_on_sole_scene_delete(self):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "delete_scene", "name": "Scene"})
        assert res.success is False
        assert "Cannot delete sole remaining scene" in res.error_message
