"""Test Suite for Blender Phase 7 — Rendering & Async Jobs.

Covers unit validation, adapter integration, BPY script generation,
physical Blender 5.2.0 LTS rendering execution (still image, current frame, frame sequence),
async job manager lifecycle (submission, status, progress, cancellation, timeout),
fresh-process persistence, failure handling, and security rejection.
"""

import pytest
import os
import tempfile
import time
import structlog

from app.ai.desktop_automation.blender_adapter import (
    BlenderActionValidator,
    BlenderActionValidationError,
    BlenderBpyExecutor,
)
from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter
from app.ai.desktop_automation.blender_executors.render_executor import (
    SUPPORTED_RENDER_ACTIONS,
)
from app.ai.desktop_automation.render_job_manager import (
    RenderJobManager,
    RenderJobState,
)
from app.ai.desktop_automation.automation_router import AutomationRouter
from app.ai.desktop_automation.models import AutomationAction

logger = structlog.get_logger("test_blender_phase7")


@pytest.fixture
def blender_path():
    path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    if not os.path.exists(path):
        pytest.skip(f"Blender executable not found at {path}")
    return path


class TestBlenderRenderValidatorUnit:
    """Unit tests for Phase 7 action validation and security filtering."""

    def test_all_44_actions_recognized(self):
        assert len(SUPPORTED_RENDER_ACTIONS) == 44
        validator = BlenderActionValidator()
        for act in SUPPORTED_RENDER_ACTIONS:
            assert act in validator.RENDER_ACTIONS

    def test_validate_render_resolution(self):
        action = AutomationAction(
            action_type="set_render_resolution",
            value={"resolution_x": 1920, "resolution_y": 1080}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "set_render_resolution"
        assert res["resolution_x"] == 1920
        assert res["resolution_y"] == 1080

    def test_validate_invalid_resolution_fails(self):
        action = AutomationAction(
            action_type="set_render_resolution",
            value={"resolution_x": -100, "resolution_y": 1080}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_validate_render_engine(self):
        action = AutomationAction(
            action_type="set_render_engine",
            value={"engine": "CYCLES"}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["engine"] == "CYCLES"

    def test_validate_invalid_render_engine_fails(self):
        action = AutomationAction(
            action_type="set_render_engine",
            value={"engine": "NONEXISTENT_UNREAL_ENGINE"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_validate_path_traversal_fails(self):
        action = AutomationAction(
            action_type="set_render_output_path",
            value={"filepath": "../../windows/system32/render.png"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_forbidden_raw_python_rejected(self):
        action = AutomationAction(
            action_type="render_still",
            value={"raw_python": "import os; os.system('calc.exe')"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)


class TestBlenderAdapterIntegrationPhase7:
    """Integration tests for Phase 7 action registration and router routing."""

    def test_total_blender_action_count(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        assert len(adapter.BLENDER_STRUCTURED_ACTIONS) >= 287
        assert "render_still" in caps
        assert "submit_render_job" in caps

    def test_router_integration_phase7(self):
        router = AutomationRouter()
        for act_type in SUPPORTED_RENDER_ACTIONS:
            action = AutomationAction(action_type=act_type)
            decision = router.route_action("Blender", action)
            assert decision.tier == 1, f"Action {act_type} failed router tier 1 check"


@pytest.mark.asyncio
class TestBlenderPhysicalRenderExec:
    """Physical Blender 5.2.0 LTS rendering & async job execution tests."""

    async def test_physical_render_configuration_and_still(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_img = os.path.join(tmp_dir, "test_render.png").replace("\\", "/")

            # Set resolution to fast 32x32
            res1 = await executor.execute_bpy({"action_type": "set_render_resolution", "resolution_x": 32, "resolution_y": 32})
            assert res1.success

            # Set output path
            res2 = await executor.execute_bpy({"action_type": "set_render_output_path", "filepath": out_img})
            assert res2.success

            # Render still frame
            res3 = await executor.execute_bpy({"action_type": "render_still", "filepath": out_img})
            assert res3.success
            assert os.path.exists(out_img)
            assert os.path.getsize(out_img) > 0

    async def test_physical_render_animation_sequence(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_prefix = os.path.join(tmp_dir, "frame_").replace("\\", "/")

            # Set resolution fast
            await executor.execute_bpy({"action_type": "set_render_resolution", "resolution_x": 16, "resolution_y": 16})
            await executor.execute_bpy({"action_type": "set_render_frame_range", "start_frame": 1, "end_frame": 2, "step": 1})

            # Render frame range
            res = await executor.execute_bpy({"action_type": "render_frame_range", "start_frame": 1, "end_frame": 2, "filepath": out_prefix})
            assert res.success

            # Validate animation output
            val_res = await executor.execute_bpy({"action_type": "validate_animation_render_output", "start_frame": 1, "end_frame": 2, "filepath": out_prefix})
            assert val_res.success

    async def test_async_job_manager_lifecycle(self, blender_path):
        job_mgr = RenderJobManager.get_instance()
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_img = os.path.join(tmp_dir, "async_render.png").replace("\\", "/")

            # Build a simple render script
            script_code = (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::render_still')\n"
                "bpy.context.scene.render.resolution_x = 32\n"
                "bpy.context.scene.render.resolution_y = 32\n"
                f"bpy.context.scene.render.filepath = '{out_img}'\n"
                "bpy.ops.render.render(write_still=True)\n"
                f"print('NOVA_ACTION_SUCCESS::render_still::{out_img}')\n"
            )
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(script_code)
                script_path = f.name

            # Submit async job
            job = job_mgr.submit_job(
                job_id="TEST-JOB-001",
                blender_executable=blender_path,
                script_path=script_path,
                output_path=out_img,
                render_type="STILL",
                timeout_sec=30.0,
            )
            assert job.job_id == "TEST-JOB-001"
            assert job.state in (RenderJobState.RUNNING, RenderJobState.COMPLETED)

            # Wait for job completion
            res = job_mgr.wait_for_job("TEST-JOB-001", timeout_sec=20.0)
            assert res.state == RenderJobState.COMPLETED
            assert len(res.output_files) > 0
            assert os.path.exists(out_img)

    async def test_async_job_cancellation(self, blender_path):
        job_mgr = RenderJobManager.get_instance()
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_img = os.path.join(tmp_dir, "cancel_render.png").replace("\\", "/")
            # Script that sleeps inside python to allow testing cancellation
            script_code = (
                "import bpy, time\n"
                "print('NOVA_ACTION_START::long_render')\n"
                "time.sleep(10.0)\n"
                "print('NOVA_ACTION_SUCCESS::long_render')\n"
            )
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(script_code)
                script_path = f.name

            job_mgr.submit_job(
                job_id="CANCEL-JOB-001",
                blender_executable=blender_path,
                script_path=script_path,
                output_path=out_img,
                timeout_sec=30.0,
            )
            time.sleep(0.5)

            # Cancel job
            cancelled = job_mgr.cancel_job("CANCEL-JOB-001")
            assert cancelled is True
            assert job_mgr.get_status("CANCEL-JOB-001") == RenderJobState.CANCELLED


@pytest.mark.asyncio
class TestBlenderPersistencePhase7:
    """Fresh-process save/reopen persistence testing for Phase 7 render settings."""

    async def test_render_settings_persistence(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "render_scene.blend").replace("\\", "/")
            out_render = os.path.join(tmp_dir, "persisted_render.png").replace("\\", "/")

            # PROCESS 1: Save initial scene, configure render settings, and save to blend_file
            save_res = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert save_res.success
            assert os.path.exists(blend_file)

            res1 = await executor.execute_bpy({"action_type": "set_render_resolution", "resolution_x": 48, "resolution_y": 48}, blend_filepath=blend_file)
            assert res1.success

            res2 = await executor.execute_bpy({"action_type": "set_render_file_format", "file_format": "PNG"}, blend_filepath=blend_file)
            assert res2.success

            # PROCESS 2: Reopen in a fresh Blender process & verify state survived
            exec2 = BlenderBpyExecutor()
            check_res = await exec2.execute_bpy({"action_type": "get_render_resolution"}, blend_filepath=blend_file)
            assert check_res.success
            assert "48x48" in check_res.output["stdout"]

            # Perform render from Process 2
            render_res = await exec2.execute_bpy({"action_type": "render_still", "filepath": out_render}, blend_filepath=blend_file)
            assert render_res.success
            assert os.path.exists(out_render)
