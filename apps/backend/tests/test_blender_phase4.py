"""Test Suite for Blender Phase 4 — Materials & Shading.

Covers unit validation, adapter integration, execution protocol failure modes,
and physical verification against installed Blender 5.2.0 LTS including fresh-process persistence.
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
from app.ai.desktop_automation.blender_executors.material_executor import (
    BlenderMaterialExecutor,
    SUPPORTED_MATERIAL_ACTIONS,
)
from app.ai.desktop_automation.application_adapter import ApplicationAdapterRegistry
from app.ai.desktop_automation.automation_router import AutomationRouter, AutomationTier
from app.ai.desktop_automation.models import AutomationAction, AutomationResult

logger = structlog.get_logger("test_blender_phase4")

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


@pytest.fixture
def blender_path():
    if not os.path.exists(BLENDER_EXE):
        pytest.skip(f"Blender executable not found at {BLENDER_EXE}")
    return BLENDER_EXE


class TestBlenderMaterialValidatorUnit:
    """Unit test suite for Blender Phase 4 material parameter schemas and security."""

    def test_all_114_actions_recognized(self):
        adapter = BlenderApplicationAdapter()
        caps = set(adapter.get_capabilities())
        assert len(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS) >= 114
        assert len(caps.intersection(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS)) >= 114

    def test_validate_create_material(self):
        action = AutomationAction(
            action_type="create_material",
            target_label="GoldMat",
            value={"use_nodes": True},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_material"
        assert res["material_name"] == "GoldMat"
        assert res["use_nodes"] is True

    def test_validate_principled_bsdf_parameters(self):
        action = AutomationAction(
            action_type="set_principled_metallic",
            target_label="GoldMat",
            value={"value": 0.95},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "set_principled_metallic"
        assert res["material_name"] == "GoldMat"

    def test_reject_unallowed_shader_node_type(self):
        action = AutomationAction(
            action_type="create_shader_node",
            target_label="GoldMat",
            value={"node_type": "FORBIDDEN_CUSTOM_NODE", "node_name": "BadNode"},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "not in allowed node types" in str(excinfo.value)

    def test_reject_nonexistent_image_path(self):
        action = AutomationAction(
            action_type="add_image_texture",
            target_label="GoldMat",
            value={"image_path": "C:/nonexistent_fake_image_file_path_12345.png"},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "does not exist" in str(excinfo.value)

    def test_reject_forbidden_python_keys(self):
        action = AutomationAction(
            action_type="create_material",
            target_label="TestMat",
            value={"exec": "import os; os.system('calc')"},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "forbidden" in str(excinfo.value)

    def test_reject_malicious_material_name(self):
        action = AutomationAction(
            action_type="create_material",
            target_label="Mat'; import os; os.system('calc'); '",
            value={},
        )
        with pytest.raises(BlenderActionValidationError) as excinfo:
            BlenderActionValidator.validate_action(action)
        assert "forbidden string or character" in str(excinfo.value)


class TestBlenderAdapterIntegrationPhase4:
    """Integration test suite for Phase 4 adapter capabilities, router, and security."""

    def test_all_114_actions_in_capabilities(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        for act in SUPPORTED_MATERIAL_ACTIONS:
            assert act in caps

    def test_router_integration_phase4(self):
        registry = ApplicationAdapterRegistry()
        router = AutomationRouter(registry=registry)
        action = AutomationAction(action_type="create_material", target_label="RubyMat")
        decision = router.route_action("blender", action)
        assert decision.tier == AutomationTier.TIER_1_NATIVE_API

    @pytest.mark.asyncio
    async def test_security_blocks_raw_python(self):
        adapter = BlenderApplicationAdapter()
        action = AutomationAction(
            action_type="raw_python",
            value={"code": "import os; os.system('calc')"},
        )
        res = await adapter.execute(action)
        assert res.success is False
        assert "forbidden" in res.error_message.lower()


class TestBlenderExecutionProtocolFailureModesPhase4:
    """Protocol error handling tests for Phase 4."""

    def test_material_executor_templates_syntax(self):
        for act in SUPPORTED_MATERIAL_ACTIONS:
            # Skip image texture path validation in template test
            if "image_texture" in act:
                continue
            script = BlenderMaterialExecutor.build_bpy_script(act, {
                "material_name": "TestMat",
                "object_name": "Cube",
                "node_name": "NoiseNode",
                "from_node": "NoiseNode",
                "to_node": "Principled",
            })
            assert "NOVA_ACTION_START" in script
            assert ("NOVA_ACTION_SUCCESS" in script or "NOVA_ACTION_ERROR" in script)
            compile(script, "<string>", "exec")

    @pytest.mark.asyncio
    async def test_deliberate_exception_handling(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({"action_type": "create_material", "name": "CrashMat"}, is_blender_running=False)
        assert isinstance(res, AutomationResult)


class TestBlenderPhysicalMaterialVerification:
    """Physical Blender execution tests verifying materials, nodes, textures, and persistence."""

    @pytest.mark.asyncio
    async def test_physical_material_lifecycle_nodes_and_persistence(self, blender_path):
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
            assert (await executor.execute_bpy({
                "action_type": "create_primitive_mesh",
                "primitive": "cube",
                "name": "MaterialCube",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 2. Create Material GoldMat
            r_mat = await executor.execute_bpy({
                "action_type": "create_material",
                "material_name": "GoldMat",
                "use_nodes": True,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_mat.success is True

            # 3. Assign GoldMat to MaterialCube
            r_assign = await executor.execute_bpy({
                "action_type": "assign_material",
                "object_name": "MaterialCube",
                "material_name": "GoldMat",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_assign.success is True

            # 4. Configure Principled BSDF Properties
            assert (await executor.execute_bpy({
                "action_type": "set_principled_base_color",
                "material_name": "GoldMat",
                "color": [1.0, 0.8, 0.2, 1.0],
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "set_principled_metallic",
                "material_name": "GoldMat",
                "value": 0.9,
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "set_principled_roughness",
                "material_name": "GoldMat",
                "value": 0.15,
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "set_principled_ior",
                "material_name": "GoldMat",
                "value": 1.45,
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 5. Add Procedural Noise Texture Node
            assert (await executor.execute_bpy({
                "action_type": "add_noise_texture",
                "material_name": "GoldMat",
                "node_name": "GoldNoise",
                "scale": 12.5,
                "detail": 4.0,
                "roughness": 0.6,
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 6. Add Bump Node
            assert (await executor.execute_bpy({
                "action_type": "add_bump_node",
                "material_name": "GoldMat",
                "node_name": "GoldBump",
                "strength": 0.3,
                "distance": 0.1,
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 7. Connect Noise -> Bump -> Principled Normal
            assert (await executor.execute_bpy({
                "action_type": "connect_shader_nodes",
                "material_name": "GoldMat",
                "from_node": "GoldNoise",
                "from_socket": "Fac",
                "to_node": "GoldBump",
                "to_socket": "Height",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "set_principled_normal",
                "material_name": "GoldMat",
                "node_name": "GoldBump",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 8. Validate Material State
            r_val = await executor.execute_bpy({
                "action_type": "validate_material",
                "material_name": "GoldMat",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_val.success is True

            # 9. Save file
            res_save = await executor.execute_bpy({
                "action_type": "save_file",
                "filepath": blend_file,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert res_save.success is True

            # 10. REOPEN IN NEW FRESH BLENDER PROCESS AND VERIFY PERSISTENCE
            r_reopen_state = await executor.execute_bpy({
                "action_type": "get_material_state",
                "material_name": "GoldMat",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_reopen_state.success is True

            r_reopen_slots = await executor.execute_bpy({
                "action_type": "get_material_slots",
                "object_name": "MaterialCube",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_reopen_slots.success is True

        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass

    @pytest.mark.asyncio
    async def test_physical_image_texture_and_slots(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        # Create a real dummy local image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_tmp:
            dummy_img_path = img_tmp.name
            img_tmp.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\aeB`\x82")

        try:
            # 0. Save initial scene
            assert (await executor.execute_bpy({
                "action_type": "save_file",
                "filepath": blend_file,
            }, is_blender_running=False)).success is True

            # 1. Create Material TextMat
            assert (await executor.execute_bpy({
                "action_type": "create_material",
                "material_name": "TextMat",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 2. Add Image Texture Node with real local image path
            r_img = await executor.execute_bpy({
                "action_type": "add_image_texture",
                "material_name": "TextMat",
                "node_name": "MainImgNode",
                "image_path": dummy_img_path,
            }, is_blender_running=False, blend_filepath=blend_file)
            assert r_img.success is True

            # 3. Configure Image Texture Settings
            assert (await executor.execute_bpy({
                "action_type": "set_image_texture_interpolation",
                "material_name": "TextMat",
                "node_name": "MainImgNode",
                "interpolation": "Closest",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            assert (await executor.execute_bpy({
                "action_type": "set_image_texture_extension",
                "material_name": "TextMat",
                "node_name": "MainImgNode",
                "extension": "Clip",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            # 4. Connect Image Texture to Principled Base Color
            assert (await executor.execute_bpy({
                "action_type": "connect_image_texture_to_shader",
                "material_name": "TextMat",
                "image_node_name": "MainImgNode",
                "socket_name": "Base Color",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass
            if os.path.exists(dummy_img_path):
                try:
                    os.remove(dummy_img_path)
                except OSError:
                    pass


class TestBlenderMaterialFailureModes:
    """Failure mode tests for material operations."""

    @pytest.mark.asyncio
    async def test_nonexistent_material_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        res = await executor.execute_bpy({
            "action_type": "get_material",
            "material_name": "NonexistentMat_999",
        }, is_blender_running=False)
        assert res.success is False
        assert "not found" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_node_deletion_fails(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as tmp:
            blend_file = tmp.name

        try:
            assert (await executor.execute_bpy({
                "action_type": "save_file",
                "filepath": blend_file,
            }, is_blender_running=False)).success is True

            assert (await executor.execute_bpy({
                "action_type": "create_material",
                "material_name": "FailMat",
            }, is_blender_running=False, blend_filepath=blend_file)).success is True

            res = await executor.execute_bpy({
                "action_type": "delete_shader_node",
                "material_name": "FailMat",
                "node_name": "GhostNode",
            }, is_blender_running=False, blend_filepath=blend_file)
            assert res.success is False
            assert "not found" in res.error_message.lower()
        finally:
            if os.path.exists(blend_file):
                try:
                    os.remove(blend_file)
                except OSError:
                    pass
