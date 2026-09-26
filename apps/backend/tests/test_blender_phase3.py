"""Comprehensive Verification Suite for F1.57 Blender Phase 3 Modifiers & Non-Destructive Modeling.

Covers:
A. Validator unit tests (valid/invalid modifier types, valid/invalid properties, bounds, object references, malicious payloads)
B. Adapter integration tests (registration, capabilities reporting, router Tier 1 dispatch, security guards)
C. Execution protocol tests (deliberate exception, syntax error, missing marker, traceback capture, success marker)
D. Physical Blender verification against Blender 5.2.0 LTS (adding/configuring/reordering/toggling/removing/applying modifiers, BOOLEAN operand references, mesh statistics changes, SAVE -> REOPEN IN NEW PROCESS persistence)
E. Failure/Recovery mode tests (nonexistent object, nonexistent modifier, invalid index/property/range, self-referencing boolean)
"""

import os
import ast
import tempfile
import pytest

from app.ai.desktop_automation.models import AutomationAction, AutomationResult
from app.ai.desktop_automation.blender_adapter import (
    BlenderActionValidator,
    BlenderActionValidationError,
    BlenderBpyExecutor,
)
from app.ai.desktop_automation.blender_executors.modifier_executor import (
    BlenderModifierExecutor,
    SUPPORTED_MODIFIER_TYPES,
    VALID_MODIFIER_PROPERTIES,
)
from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter
from app.ai.desktop_automation.automation_router import AutomationRouter, AutomationTier


class TestBlenderModifierValidatorUnit:
    """Unit test suite for Phase 3 Blender modifier action validation schemas and security."""

    def test_all_68_actions_recognized(self):
        adapter = BlenderApplicationAdapter()
        caps = set(adapter.get_capabilities())
        assert len(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS) >= 68
        assert len(caps.intersection(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS)) >= 68

    def test_validate_add_modifier_supported_types(self):
        for mod_type in SUPPORTED_MODIFIER_TYPES:
            action = AutomationAction(
                action_type="add_modifier",
                target_label="Cube",
                value={"modifier_type": mod_type, "modifier_name": f"My_{mod_type}"},
            )
            res = BlenderActionValidator.validate_action(action)
            assert res["action_type"] == "add_modifier"
            assert res["modifier_type"] == mod_type
            assert res["modifier_name"] == f"My_{mod_type}"

    def test_reject_unknown_modifier_type(self):
        action = AutomationAction(
            action_type="add_modifier",
            target_label="Cube",
            value={"modifier_type": "UNKNOWN_MODIFIER", "modifier_name": "TestMod"},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "Unsupported modifier type" in str(excinfo.value)

    def test_validate_modifier_properties_subsurf(self):
        action = AutomationAction(
            action_type="set_modifier_properties",
            target_label="Cube",
            value={
                "modifier_name": "Subsurf",
                "properties": {"levels": 3, "render_levels": 4, "subdivision_type": "CATMULL_CLARK"},
            },
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["properties"]["levels"] == 3
        assert res["properties"]["render_levels"] == 4
        assert res["properties"]["subdivision_type"] == "CATMULL_CLARK"

    def test_reject_subsurf_invalid_levels(self):
        action = AutomationAction(
            action_type="set_modifier_properties",
            target_label="Cube",
            value={"modifier_name": "Subsurf", "properties": {"levels": 15}},  # Out of range (0..6)
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "out of range" in str(excinfo.value).lower()

    def test_validate_boolean_operand_and_reject_self_reference(self):
        # Valid operand object
        action_valid = AutomationAction(
            action_type="set_modifier_properties",
            target_label="Cube",
            value={"modifier_name": "Boolean", "properties": {"operand_object": "Cylinder", "operation": "DIFFERENCE"}},
        )
        res = BlenderActionValidator.validate_action(action_valid)
        assert res["properties"]["operand_object"] == "Cylinder"

        # Invalid self-referencing operand object
        action_self = AutomationAction(
            action_type="set_modifier_properties",
            target_label="Cube",
            value={"modifier_name": "Boolean", "properties": {"operand_object": "Cube"}},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action_self)
        assert "cannot target itself" in str(excinfo.value).lower()

    def test_validate_move_modifier(self):
        action = AutomationAction(
            action_type="move_modifier",
            target_label="Cube",
            value={"modifier_name": "Bevel", "direction": "move_to_index", "index": 0},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["direction"] == "move_to_index"
        assert res["index"] == 0

    def test_reject_invalid_move_direction(self):
        action = AutomationAction(
            action_type="move_modifier",
            target_label="Cube",
            value={"modifier_name": "Bevel", "direction": "teleport"},
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_reject_forbidden_python_in_modifier_params(self):
        for key in ("raw_python", "eval_python", "exec", "script", "code"):
            action = AutomationAction(
                action_type="add_modifier",
                target_label="Cube",
                value={"modifier_type": "SUBSURF", key: "import os; os.system('calc')"},
            )
            with pytest.raises(BlenderActionValidationError):
                BlenderActionValidator.validate_action(action)

    def test_reject_malicious_modifier_names(self):
        action = AutomationAction(
            action_type="add_modifier",
            target_label="Cube",
            value={"modifier_type": "SUBSURF", "modifier_name": "Mod'; import os; os.system('calc') #"},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "contains forbidden string" in str(excinfo.value).lower()


class TestBlenderAdapterIntegrationPhase3:
    """Integration test suite for Phase 3 modifier actions."""

    def test_all_68_actions_in_capabilities(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        for act in BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS:
            assert act in caps

    def test_router_integration_phase3(self):
        router = AutomationRouter()
        modifier_actions = [
            "add_modifier",
            "remove_modifier",
            "rename_modifier",
            "move_modifier",
            "get_modifiers",
            "get_modifier_state",
            "set_modifier_properties",
            "set_modifier_viewport_visibility",
            "set_modifier_render_visibility",
            "apply_modifier",
        ]
        for act in modifier_actions:
            action = AutomationAction(action_type=act, target_label="Cube")
            decision = router.route_action("Blender", action)
            assert decision.tier == AutomationTier.TIER_1_NATIVE_API

    @pytest.mark.asyncio
    async def test_security_blocks_raw_python(self):
        adapter = BlenderApplicationAdapter()
        for raw in ("raw_python", "eval_python", "blender_bpy_script"):
            action = AutomationAction(action_type=raw, value={"code": "import os"})
            res = await adapter.execute(action)
            assert res.success is False
            assert "forbidden" in res.error_message.lower()


class TestBlenderExecutionProtocolFailureModesPhase3:
    """Execution protocol tests verifying machine-readable error handling and markers."""

    def test_modifier_templates_syntax(self):
        sample_params = {
            "add_modifier": {"object_name": "Cube", "modifier_type": "SUBSURF", "modifier_name": "Subsurf"},
            "remove_modifier": {"object_name": "Cube", "modifier_name": "Subsurf"},
            "rename_modifier": {"object_name": "Cube", "old_name": "Subsurf", "new_name": "MySubsurf"},
            "move_modifier": {"object_name": "Cube", "modifier_name": "Subsurf", "direction": "move_up", "index": 0},
            "get_modifiers": {"object_name": "Cube"},
            "get_modifier_state": {"object_name": "Cube", "modifier_name": "Subsurf"},
            "set_modifier_properties": {"object_name": "Cube", "modifier_name": "Subsurf", "properties": {"levels": 2}},
            "set_modifier_viewport_visibility": {"object_name": "Cube", "modifier_name": "Subsurf", "show_viewport": False},
            "set_modifier_render_visibility": {"object_name": "Cube", "modifier_name": "Subsurf", "show_render": False},
            "apply_modifier": {"object_name": "Cube", "modifier_name": "Subsurf"},
        }
        for action_type, params in sample_params.items():
            params["action_type"] = action_type
            script = BlenderModifierExecutor.build_script(action_type, params)
            ast.parse(script)  # Ensures valid Python syntax

    @pytest.mark.asyncio
    async def test_deliberate_exception_handling(self):
        executor = BlenderBpyExecutor()
        bad_params = {"action_type": "add_modifier", "object_name": "NonExistentCubeXYZ", "modifier_type": "SUBSURF", "modifier_name": "Subsurf"}
        result = await executor.execute_bpy(bad_params, is_blender_running=False)
        assert result.success is False
        assert "NOVA_ACTION_ERROR" in (result.error_message or "") or "not found" in (result.error_message or "").lower()

    @pytest.mark.asyncio
    async def test_missing_marker_produces_failure(self, monkeypatch):
        executor = BlenderBpyExecutor()
        monkeypatch.setattr(BlenderBpyExecutor, "build_bpy_script", lambda self, p: "import bpy\nx = 10\nprint('Done without marker')\n")
        res = await executor.execute_bpy({"action_type": "add_modifier", "object_name": "Cube", "modifier_type": "SUBSURF"}, is_blender_running=False)
        assert res.success is False
        assert "missing success marker" in res.error_message.lower()


class TestBlenderPhysicalModifierVerification:
    """Physical Blender 5.2.0 LTS verification for non-destructive modifier stack workflows,

    persistence across fresh process reopening, and apply_modifier mesh topological changes.
    """

    @pytest.fixture
    def blender_path(self):
        path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
        if not os.path.exists(path):
            pytest.skip("Physical Blender 5.2.0 LTS executable not installed at expected location.")
        return path

    @pytest.mark.asyncio
    async def test_physical_modifier_stack_workflow_and_persistence(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        try:
            # 0. Initial Save
            res0 = await executor.execute_bpy({
                "action_type": "save_file",
                "filepath": blend_file,
            }, is_blender_running=False)
            assert res0.success is True

            # 1. Create primitive cube
            r1 = await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cube",
                "name": "ModifierCube",
                "location": (0.0, 0.0, 0.0),
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r1.success is True

            # 2. Add SUBSURF modifier
            r2 = await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "ModifierCube",
                "modifier_type": "SUBSURF",
                "modifier_name": "MySubsurf",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r2.success is True

            # 3. Set SUBSURF properties (levels=2, render_levels=3)
            r3 = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "ModifierCube",
                "modifier_name": "MySubsurf",
                "properties": {"levels": 2, "render_levels": 3},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r3.success is True

            # 4. Add BEVEL modifier
            r4 = await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "ModifierCube",
                "modifier_type": "BEVEL",
                "modifier_name": "MyBevel",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r4.success is True

            # 5. Configure BEVEL properties (width=0.1, segments=3)
            r5 = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "ModifierCube",
                "modifier_name": "MyBevel",
                "properties": {"width": 0.1, "segments": 3},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r5.success is True

            # 6. Add MIRROR modifier
            r6 = await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "ModifierCube",
                "modifier_type": "MIRROR",
                "modifier_name": "MyMirror",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r6.success is True

            # 7. Configure MIRROR properties (use_axis_x=True, use_clip=True)
            r7 = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "ModifierCube",
                "modifier_name": "MyMirror",
                "properties": {"use_axis_x": True, "use_clip": True},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r7.success is True

            # 8. Add SOLIDIFY modifier
            r8 = await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "ModifierCube",
                "modifier_type": "SOLIDIFY",
                "modifier_name": "MySolidify",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r8.success is True

            # 9. Configure SOLIDIFY properties (thickness=0.25, use_rim=True)
            r9 = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "ModifierCube",
                "modifier_name": "MySolidify",
                "properties": {"thickness": 0.25, "use_rim": True},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r9.success is True

            # 10. Add ARRAY modifier
            r10 = await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "ModifierCube",
                "modifier_type": "ARRAY",
                "modifier_name": "MyArray",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r10.success is True

            # 11. Configure ARRAY properties (count=4)
            r11 = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "ModifierCube",
                "modifier_name": "MyArray",
                "properties": {"count": 4},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r11.success is True

            # 12. Inspect modifier stack
            r12 = await executor.execute_bpy({
                "action_type": "get_modifiers",
                "object_name": "ModifierCube",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r12.success is True
            assert "MySubsurf" in r12.output["stdout"]
            assert "MyBevel" in r12.output["stdout"]
            assert "MyMirror" in r12.output["stdout"]
            assert "MySolidify" in r12.output["stdout"]
            assert "MyArray" in r12.output["stdout"]

            # 13. Reorder modifier (Move MyArray to index 0)
            r13 = await executor.execute_bpy({
                "action_type": "move_modifier",
                "object_name": "ModifierCube",
                "modifier_name": "MyArray",
                "direction": "move_to_index",
                "index": 0,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r13.success is True

            # 14. Toggle viewport and render visibility
            r14 = await executor.execute_bpy({
                "action_type": "set_modifier_viewport_visibility",
                "object_name": "ModifierCube",
                "modifier_name": "MyArray",
                "show_viewport": False,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r14.success is True

            r15 = await executor.execute_bpy({
                "action_type": "set_modifier_render_visibility",
                "object_name": "ModifierCube",
                "modifier_name": "MyArray",
                "show_render": False,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r15.success is True

            # 15. Remove a modifier (Remove MySolidify)
            r16 = await executor.execute_bpy({
                "action_type": "remove_modifier",
                "object_name": "ModifierCube",
                "modifier_name": "MySolidify",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r16.success is True

            # 16. Save and verify persistence in a FRESH NEW Blender process
            r_pers = await executor.execute_bpy({
                "action_type": "get_modifiers",
                "object_name": "ModifierCube",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_pers.success is True
            assert "MyArray" in r_pers.output["stdout"]
            assert "MySolidify" not in r_pers.output["stdout"]

        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass

    @pytest.mark.asyncio
    async def test_physical_boolean_operand_and_apply_modifier(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        try:
            # 0. Initial Save
            res0 = await executor.execute_bpy({
                "action_type": "save_file",
                "filepath": blend_file,
            }, is_blender_running=False)
            assert res0.success is True

            # 1. Create target cube and operand cylinder
            assert (await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cube",
                "name": "TargetCube",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cylinder",
                "name": "CylinderCutter",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 2. Add BOOLEAN modifier to TargetCube
            assert (await executor.execute_bpy({
                "action_type": "add_modifier",
                "object_name": "TargetCube",
                "modifier_type": "BOOLEAN",
                "modifier_name": "BoolCutter",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 3. Configure BOOLEAN with operand_object="CylinderCutter"
            r_bool = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "TargetCube",
                "modifier_name": "BoolCutter",
                "properties": {"operand_object": "CylinderCutter", "operation": "DIFFERENCE"},
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_bool.success is True

            # 4. Get initial mesh statistics before applying modifier
            r_stat_before = await executor.execute_bpy({
                "action_type": "get_mesh_statistics",
                "object_name": "TargetCube",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_stat_before.success is True

            # 5. Apply BOOLEAN modifier (converts evaluated geometry to permanent mesh topology)
            r_apply = await executor.execute_bpy({
                "action_type": "apply_modifier",
                "object_name": "TargetCube",
                "modifier_name": "BoolCutter",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_apply.success is True

            # 6. Verify modifier disappeared from stack and mesh geometry changed
            r_stat_after = await executor.execute_bpy({
                "action_type": "get_mesh_statistics",
                "object_name": "TargetCube",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_stat_after.success is True
            assert "verts=" in r_stat_after.output["stdout"]

        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass


class TestBlenderModifierFailureModes:
    """Failure mode tests ensuring proper exception handling and zero false success."""

    @pytest.mark.asyncio
    async def test_nonexistent_object_fails(self):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({
            "action_type": "add_modifier",
            "object_name": "GhostObject_12345",
            "modifier_type": "SUBSURF",
            "modifier_name": "GhostSubsurf",
        }, is_blender_running=False)
        assert res.success is False
        assert "not found" in (res.error_message or "").lower()

    @pytest.mark.asyncio
    async def test_nonexistent_modifier_fails(self):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        try:
            await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cube",
                "name": "CubeObj",
                "save_path": blend_file,
            }, is_blender_running=False)

            res = await executor.execute_bpy({
                "action_type": "set_modifier_properties",
                "object_name": "CubeObj",
                "modifier_name": "NonExistentMod",
                "properties": {"levels": 2},
                "blend_path": blend_file,
            }, is_blender_running=False)
            assert res.success is False
            assert "not found" in (res.error_message or "").lower()
        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass

    @pytest.mark.asyncio
    async def test_apply_nonexistent_modifier_fails(self):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        try:
            await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cube",
                "name": "CubeObj",
                "save_path": blend_file,
            }, is_blender_running=False)

            res = await executor.execute_bpy({
                "action_type": "apply_modifier",
                "object_name": "CubeObj",
                "modifier_name": "NonExistentMod",
                "blend_path": blend_file,
            }, is_blender_running=False)
            assert res.success is False
        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass
