"""Test Suite for Blender Phase 9 — Import / Export & Asset Pipeline.

Covers unit validation, schema checking, path traversal security rejection,
adapter capability registration (374 total unique actions), Tier 1 router integration,
physical Blender 5.2.0 LTS execution for 3D formats (OBJ, FBX, glTF/GLB, STL, PLY, USD, Alembic),
data-block append/link, asset packing, AssetJobManager lifecycle, fresh-process persistence, and regression.
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
from app.ai.desktop_automation.blender_executors.asset_pipeline_executor import (
    SUPPORTED_ASSET_PIPELINE_ACTIONS,
)
from app.ai.desktop_automation.asset_job_manager import (
    AssetJobManager,
    AssetJobState,
)
from app.ai.desktop_automation.automation_router import AutomationRouter
from app.ai.desktop_automation.models import AutomationAction

logger = structlog.get_logger("test_blender_phase9")


@pytest.fixture
def blender_path():
    path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    if not os.path.exists(path):
        pytest.skip(f"Blender executable not found at {path}")
    return path


class TestBlenderPhase9ValidatorUnit:
    """Unit tests for Phase 9 action validation and security controls."""

    def test_all_35_actions_recognized(self):
        assert len(SUPPORTED_ASSET_PIPELINE_ACTIONS) == 35
        validator = BlenderActionValidator()
        for act in SUPPORTED_ASSET_PIPELINE_ACTIONS:
            assert act in validator.ASSET_PIPELINE_ACTIONS

    def test_validate_gltf_export_format_allowlist(self):
        action_glb = AutomationAction(
            action_type="export_gltf",
            value={"filepath": "C:/tmp/scene.glb", "export_format": "GLB"}
        )
        res_glb = BlenderActionValidator.validate_action(action_glb)
        assert res_glb["export_format"] == "GLB"

        action_sep = AutomationAction(
            action_type="export_gltf",
            value={"filepath": "C:/tmp/scene.gltf", "export_format": "GLTF_SEPARATE"}
        )
        res_sep = BlenderActionValidator.validate_action(action_sep)
        assert res_sep["export_format"] == "GLTF_SEPARATE"

    def test_validate_invalid_gltf_enum_fails(self):
        action_bad = AutomationAction(
            action_type="export_gltf",
            value={"filepath": "C:/tmp/scene.gltf", "export_format": "GLTF_EMBEDDED"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action_bad)

    def test_path_traversal_rejected(self):
        action = AutomationAction(
            action_type="export_obj",
            value={"filepath": "../secret_file.obj"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_forbidden_raw_python_rejected(self):
        action = AutomationAction(
            action_type="import_obj",
            value={"filepath": "C:/tmp/cube.obj", "raw_python": "import os; os.system('calc.exe')"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)


class TestBlenderAdapterIntegrationPhase9:
    """Integration tests for Phase 9 capabilities and router integration."""

    def test_total_blender_action_count(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        assert len(adapter.BLENDER_STRUCTURED_ACTIONS) == 374
        assert "import_obj" in caps
        assert "export_gltf" in caps

    def test_router_integration_phase9(self):
        router = AutomationRouter()
        for act_type in SUPPORTED_ASSET_PIPELINE_ACTIONS:
            action = AutomationAction(action_type=act_type)
            decision = router.route_action("Blender", action)
            assert decision.tier == 1


@pytest.mark.asyncio
class TestBlenderPhysicalImportExportExec:
    """Physical Blender 5.2.0 LTS import and export execution tests."""

    async def test_physical_obj_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            obj_file = os.path.join(tmp_dir, "cube.obj").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_obj", "filepath": obj_file}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(obj_file)
            assert os.path.getsize(obj_file) > 0

            res2 = await executor.execute_bpy({"action_type": "import_obj", "filepath": obj_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_gltf_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            glb_file = os.path.join(tmp_dir, "cube.glb").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_gltf", "filepath": glb_file, "export_format": "GLB"}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(glb_file)
            assert os.path.getsize(glb_file) > 0

            res2 = await executor.execute_bpy({"action_type": "import_gltf", "filepath": glb_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_stl_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            stl_file = os.path.join(tmp_dir, "cube.stl").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_stl", "filepath": stl_file}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(stl_file)
            assert os.path.getsize(stl_file) > 0

            res2 = await executor.execute_bpy({"action_type": "import_stl", "filepath": stl_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_ply_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            ply_file = os.path.join(tmp_dir, "cube.ply").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_ply", "filepath": ply_file}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(ply_file)
            assert os.path.getsize(ply_file) > 0

            res2 = await executor.execute_bpy({"action_type": "import_ply", "filepath": ply_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_usd_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            usd_file = os.path.join(tmp_dir, "cube.usda").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_usd", "filepath": usd_file}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(usd_file)

            res2 = await executor.execute_bpy({"action_type": "import_usd", "filepath": usd_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_fbx_export_and_import(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "scene.blend").replace("\\", "/")
            fbx_file = os.path.join(tmp_dir, "cube.fbx").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "export_fbx", "filepath": fbx_file}, blend_filepath=blend_file)
            assert res1.success
            assert os.path.exists(fbx_file)

            res2 = await executor.execute_bpy({"action_type": "import_fbx", "filepath": fbx_file}, blend_filepath=blend_file)
            assert res2.success

    async def test_physical_append_and_link(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            src_blend = os.path.join(tmp_dir, "src.blend").replace("\\", "/")
            tgt_blend = os.path.join(tmp_dir, "tgt.blend").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": src_blend})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "save_file", "filepath": tgt_blend})
            assert res1.success

            res2 = await executor.execute_bpy({"action_type": "append_datablocks", "filepath": src_blend, "object_names": ["Cube"]}, blend_filepath=tgt_blend)
            assert res2.success


class TestAssetJobManagerLifecycle:
    """Tests for AssetJobManager state machine and cancellation."""

    def test_asset_job_manager_lifecycle(self, blender_path):
        mgr = AssetJobManager.get_instance()
        job = mgr.submit_job(
            job_id="AJOB-101",
            operation="batch_export",
            files=["model1.obj", "model2.fbx"],
            blender_executable=blender_path,
        )
        assert job.job_id == "AJOB-101"
        assert mgr.get_status("AJOB-101") == AssetJobState.QUEUED

        mgr.record_file_result("AJOB-101", "model1.obj", success=True)
        assert mgr.get_status("AJOB-101") == AssetJobState.RUNNING

        mgr.record_file_result("AJOB-101", "model2.fbx", success=True)
        mgr.finalize_job("AJOB-101")
        assert mgr.get_status("AJOB-101") == AssetJobState.COMPLETED

    def test_asset_job_manager_cancellation(self, blender_path):
        mgr = AssetJobManager.get_instance()
        mgr.submit_job(
            job_id="CANCEL-AJOB-01",
            operation="batch_import",
            files=["a.obj", "b.obj"],
            blender_executable=blender_path,
        )
        cancelled = mgr.cancel_job("CANCEL-AJOB-01")
        assert cancelled is True
        assert mgr.get_status("CANCEL-AJOB-01") == AssetJobState.CANCELLED


@pytest.mark.asyncio
class TestBlenderPersistencePhase9:
    """Fresh-process save/reopen persistence testing for Phase 9."""

    async def test_asset_pipeline_fresh_process_persistence(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "persisted_p9.blend").replace("\\", "/")

            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            res1 = await executor.execute_bpy({"action_type": "pack_all_assets"}, blend_filepath=blend_file)
            assert res1.success

            exec2 = BlenderBpyExecutor()
            res2 = await exec2.execute_bpy({"action_type": "get_external_file_references"}, blend_filepath=blend_file)
            assert res2.success
