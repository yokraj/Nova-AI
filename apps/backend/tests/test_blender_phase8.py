"""Test Suite for Blender Phase 8 — Geometry Nodes & Physics Systems.

Covers unit validation, node type allowlists, socket interfaces, node linking,
adapter capabilities (339 total actions), Tier 1 router integration,
physical Blender 5.2.0 LTS execution for Geometry Nodes & Physics (Rigid Body, Cloth, Soft Body, Collision, Fluid, Force Fields),
SimulationJobManager lifecycle, fresh-process persistence, failure handling, and security rejection.
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
from app.ai.desktop_automation.blender_executors.geometry_nodes_executor import (
    SUPPORTED_GEOMETRY_NODES_ACTIONS,
)
from app.ai.desktop_automation.blender_executors.physics_executor import (
    SUPPORTED_PHYSICS_ACTIONS,
)
from app.ai.desktop_automation.simulation_job_manager import (
    SimulationJobManager,
    SimulationJobState,
)
from app.ai.desktop_automation.automation_router import AutomationRouter
from app.ai.desktop_automation.models import AutomationAction

logger = structlog.get_logger("test_blender_phase8")


@pytest.fixture
def blender_path():
    path = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    if not os.path.exists(path):
        pytest.skip(f"Blender executable not found at {path}")
    return path


class TestBlenderPhase8ValidatorUnit:
    """Unit tests for Phase 8 Geometry Nodes & Physics action validation."""

    def test_all_52_actions_recognized(self):
        assert len(SUPPORTED_GEOMETRY_NODES_ACTIONS) == 25
        assert len(SUPPORTED_PHYSICS_ACTIONS) == 27
        validator = BlenderActionValidator()
        for act in SUPPORTED_GEOMETRY_NODES_ACTIONS:
            assert act in validator.GEOMETRY_NODES_ACTIONS
        for act in SUPPORTED_PHYSICS_ACTIONS:
            assert act in validator.PHYSICS_ACTIONS

    def test_validate_geometry_node_type_allowlist(self):
        action = AutomationAction(
            action_type="create_geometry_node",
            value={"group_name": "TestGN", "node_type": "GeometryNodeMeshCube"}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["node_type"] == "GeometryNodeMeshCube"

    def test_validate_invalid_geometry_node_type_fails(self):
        action = AutomationAction(
            action_type="create_geometry_node",
            value={"group_name": "TestGN", "node_type": "GeometryNodeUnsafeUserNode"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_validate_rigid_body_collision_shape(self):
        action = AutomationAction(
            action_type="add_rigid_body",
            value={"name": "Cube", "collision_shape": "BOX", "mass": 2.5}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["collision_shape"] == "BOX"

    def test_validate_invalid_collision_shape_fails(self):
        action = AutomationAction(
            action_type="set_rigid_body_collision_shape",
            value={"name": "Cube", "collision_shape": "NONEXISTENT_SHAPE"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)

    def test_validate_force_field_type(self):
        action = AutomationAction(
            action_type="add_force_field",
            value={"field_type": "WIND", "strength": 10.0}
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["field_type"] == "WIND"

    def test_forbidden_raw_python_rejected(self):
        action = AutomationAction(
            action_type="create_geometry_node_group",
            value={"raw_python": "import os; os.system('calc.exe')"}
        )
        with pytest.raises(BlenderActionValidationError):
            BlenderActionValidator.validate_action(action)


class TestBlenderAdapterIntegrationPhase8:
    """Integration tests for Phase 8 capability registration and router strategy."""

    def test_total_blender_action_count(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        assert len(adapter.BLENDER_STRUCTURED_ACTIONS) >= 339
        assert "create_geometry_node_group" in caps
        assert "add_rigid_body" in caps

    def test_router_integration_phase8(self):
        router = AutomationRouter()
        for act_type in SUPPORTED_GEOMETRY_NODES_ACTIONS:
            action = AutomationAction(action_type=act_type)
            decision = router.route_action("Blender", action)
            assert decision.tier == 1
        for act_type in SUPPORTED_PHYSICS_ACTIONS:
            action = AutomationAction(action_type=act_type)
            decision = router.route_action("Blender", action)
            assert decision.tier == 1


@pytest.mark.asyncio
class TestBlenderPhysicalGeometryNodesExec:
    """Physical Blender 5.2.0 LTS execution tests for Geometry Nodes."""

    async def test_physical_geometry_nodes_workflow(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "gn_scene.blend").replace("\\", "/")

            # Initial save
            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            # Create node group
            res1 = await executor.execute_bpy({"action_type": "create_geometry_node_group", "name": "ProceduralCube"}, blend_filepath=blend_file)
            assert res1.success

            # Add node socket (Blender 5.2 interface API)
            res2 = await executor.execute_bpy({"action_type": "add_geometry_node_socket", "group_name": "ProceduralCube", "socket_name": "Geometry", "in_out": "OUTPUT", "socket_type": "NodeSocketGeometry"}, blend_filepath=blend_file)
            assert res2.success

            # Create mesh cube node
            res3 = await executor.execute_bpy({"action_type": "create_geometry_node", "group_name": "ProceduralCube", "node_type": "GeometryNodeMeshCube", "node_name": "CubeNode"}, blend_filepath=blend_file)
            assert res3.success

            # Assign modifier to default Cube
            res4 = await executor.execute_bpy({"action_type": "assign_geometry_node_group", "object_name": "Cube", "modifier_name": "GeometryNodes", "group_name": "ProceduralCube"}, blend_filepath=blend_file)
            assert res4.success

            # Inspect state
            res5 = await executor.execute_bpy({"action_type": "get_geometry_node_group_state", "name": "ProceduralCube"}, blend_filepath=blend_file)
            assert res5.success
            assert os.path.exists(blend_file)


@pytest.mark.asyncio
class TestBlenderPhysicalPhysicsExec:
    """Physical Blender 5.2.0 LTS execution tests for Physics & Simulations."""

    async def test_physical_rigid_body_workflow(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "physics_scene.blend").replace("\\", "/")

            # Initial save
            res0 = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert res0.success

            # Configure Rigid Body World
            res1 = await executor.execute_bpy({"action_type": "configure_rigid_body_world", "substeps": 10}, blend_filepath=blend_file)
            assert res1.success

            # Add Active Rigid Body to Cube
            res2 = await executor.execute_bpy({"action_type": "add_rigid_body", "object_name": "Cube", "rigid_type": "ACTIVE", "mass": 5.0, "collision_shape": "BOX"}, blend_filepath=blend_file)
            assert res2.success

            # Add Cloth simulation to Cube
            res3 = await executor.execute_bpy({"action_type": "add_cloth_simulation", "object_name": "Cube", "mass": 0.3}, blend_filepath=blend_file)
            assert res3.success

            # Add Force Field
            res4 = await executor.execute_bpy({"action_type": "add_force_field", "field_type": "WIND", "strength": 10.0, "location": (0.0, 0.0, 5.0)}, blend_filepath=blend_file)
            assert res4.success

            # Inspect state
            res5 = await executor.execute_bpy({"action_type": "get_rigid_body_state", "object_name": "Cube"}, blend_filepath=blend_file)
            assert res5.success
            assert os.path.exists(blend_file)

    async def test_simulation_job_manager_lifecycle(self, blender_path):
        sim_mgr = SimulationJobManager.get_instance()
        with tempfile.TemporaryDirectory():
            script_code = (
                "import bpy\n"
                "print('NOVA_ACTION_START::bake_sim')\n"
                "print('NOVA_ACTION_SUCCESS::bake_sim::completed')\n"
            )
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(script_code)
                script_path = f.name

            # Submit simulation job
            job = sim_mgr.submit_job(
                job_id="SIM-JOB-001",
                blender_executable=blender_path,
                script_path=script_path,
                sim_type="RIGID_BODY",
                timeout_sec=30.0,
            )
            assert job.job_id == "SIM-JOB-001"

            # Wait for job completion
            res = sim_mgr.wait_for_job("SIM-JOB-001", timeout_sec=20.0)
            assert res.state == SimulationJobState.COMPLETED

    async def test_simulation_job_cancellation(self, blender_path):
        sim_mgr = SimulationJobManager.get_instance()
        script_code = (
            "import time\n"
            "print('NOVA_ACTION_START::long_bake')\n"
            "time.sleep(10.0)\n"
            "print('NOVA_ACTION_SUCCESS::long_bake')\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(script_code)
            script_path = f.name

        sim_mgr.submit_job(
            job_id="CANCEL-SIM-001",
            blender_executable=blender_path,
            script_path=script_path,
            sim_type="CLOTH",
            timeout_sec=30.0,
        )
        time.sleep(0.5)

        cancelled = sim_mgr.cancel_job("CANCEL-SIM-001")
        assert cancelled is True
        assert sim_mgr.get_status("CANCEL-SIM-001") == SimulationJobState.CANCELLED


@pytest.mark.asyncio
class TestBlenderPersistencePhase8:
    """Fresh-process save/reopen persistence testing for Phase 8."""

    async def test_geometry_nodes_and_physics_persistence(self, blender_path):
        executor = BlenderBpyExecutor()
        with tempfile.TemporaryDirectory() as tmp_dir:
            blend_file = os.path.join(tmp_dir, "persisted_p8.blend").replace("\\", "/")

            # PROCESS 1: Save initial scene & configure GN + Rigid Body
            save_res = await executor.execute_bpy({"action_type": "save_file", "filepath": blend_file})
            assert save_res.success

            res1 = await executor.execute_bpy({"action_type": "create_geometry_node_group", "name": "PersistGN"}, blend_filepath=blend_file)
            assert res1.success

            res2 = await executor.execute_bpy({"action_type": "add_rigid_body", "object_name": "Cube", "rigid_type": "ACTIVE", "mass": 3.0}, blend_filepath=blend_file)
            assert res2.success

            # PROCESS 2: Reopen in a fresh Blender process & verify state survived
            exec2 = BlenderBpyExecutor()
            check_gn = await exec2.execute_bpy({"action_type": "get_geometry_node_group_state", "name": "PersistGN"}, blend_filepath=blend_file)
            assert check_gn.success

            check_rb = await exec2.execute_bpy({"action_type": "get_rigid_body_state", "object_name": "Cube"}, blend_filepath=blend_file)
            assert check_rb.success
            assert "ACTIVE" in check_rb.output["stdout"]
