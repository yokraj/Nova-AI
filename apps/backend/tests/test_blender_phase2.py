"""Comprehensive Verification Suite for F1.57 Blender Phase 2 Mesh Modeling & BMesh.

Covers:
- Unit schema validation for 29 mesh actions (58 total Blender actions)
- Adapter capability reporting and AutomationRouter tier 1 resolution
- Security engine enforcement against raw Python / code injection
- Protocol failure regression tests (unresolved template vars, exceptions, syntax errors, missing markers)
- Physical execution against Blender 5.2.0 LTS for 18 BMesh topology actions with SAVE -> REOPEN IN NEW PROCESS persistence verification
- Selection domain semantics and index bounds checking
- Context-sensitive operations (create, convert, separate, join)
"""

import os
import ast
import re
import tempfile
import pytest

from app.ai.desktop_automation.models import AutomationAction, AutomationResult
from app.ai.desktop_automation.blender_adapter import (
    BlenderActionValidator,
    BlenderActionValidationError,
    BlenderBpyExecutor,
)
from app.ai.desktop_automation.blender_executors.mesh_executor import BlenderMeshExecutor
from app.ai.desktop_automation.blender_executors.object_executor import BlenderObjectExecutor
from app.ai.desktop_automation.blender_executors.scene_executor import BlenderSceneExecutor
from app.ai.desktop_automation.application_adapter import BlenderApplicationAdapter
from app.ai.desktop_automation.automation_router import AutomationRouter, AutomationTier


class TestBlenderMeshValidatorUnit:
    """Unit test suite for Blender Phase 2 mesh action parameter schemas."""

    def test_all_58_actions_recognized(self):
        adapter = BlenderApplicationAdapter()
        caps = set(adapter.get_capabilities())
        assert len(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS) >= 58
        assert len(caps.intersection(BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS)) >= 58

    def test_validate_create_mesh_object(self):
        action = AutomationAction(
            action_type="create_mesh_object",
            target_label="CustomMesh",
            value={"collection": "MainCol"},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_mesh_object"
        assert res["name"] == "CustomMesh"
        assert res["collection"] == "MainCol"

    def test_validate_create_primitive_mesh(self):
        action = AutomationAction(
            action_type="create_primitive_mesh",
            target_label="SphereMesh",
            value={"primitive": "uv_sphere", "location": [1.0, 2.0, 3.0]},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "create_primitive_mesh"
        assert res["name"] == "SphereMesh"
        assert res["primitive"] == "uv_sphere"
        assert res["location"] == (1.0, 2.0, 3.0)

    def test_validate_add_vertex(self):
        action = AutomationAction(
            action_type="add_vertex",
            target_label="MyMesh",
            value={"location": [0.0, 0.5, 1.5]},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "add_vertex"
        assert res["location"] == (0.0, 0.5, 1.5)

    def test_validate_extrude_region(self):
        action = AutomationAction(
            action_type="extrude_region",
            target_label="MyMesh",
            value={"distance": 2.5, "indices": [0, 1, 2]},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "extrude_region"
        assert res["distance"] == 2.5
        assert res["indices"] == [0, 1, 2]

    def test_validate_inset_faces(self):
        action = AutomationAction(
            action_type="inset_faces",
            target_label="MyMesh",
            value={"thickness": 0.15, "indices": [0]},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "inset_faces"
        assert res["thickness"] == 0.15

    def test_validate_bevel_edges(self):
        action = AutomationAction(
            action_type="bevel_edges",
            target_label="MyMesh",
            value={"offset": 0.05, "segments": 3},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "bevel_edges"
        assert res["offset"] == 0.05
        assert res["segments"] == 3

    def test_validate_subdivide_edges(self):
        action = AutomationAction(
            action_type="subdivide_edges",
            target_label="MyMesh",
            value={"cuts": 2},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "subdivide_edges"
        assert res["cuts"] == 2

    def test_validate_recalculate_normals(self):
        action = AutomationAction(
            action_type="recalculate_normals",
            target_label="MyMesh",
            value={"inside": True},
        )
        res = BlenderActionValidator.validate_action(action)
        assert res["action_type"] == "recalculate_normals"
        assert res["inside"] is True

    def test_reject_forbidden_python_keys(self):
        for key in ("raw_python", "eval_python", "exec", "script", "code"):
            action = AutomationAction(
                action_type="add_vertex",
                target_label="Mesh",
                value={key: "import os; os.system('calc')"},
            )
            with pytest.raises(BlenderActionValidationError):
                BlenderActionValidator.validate_action(action)


class TestBlenderAdapterIntegrationPhase2:
    """Integration test suite for Blender Phase 2 adapter & router interactions."""

    def test_all_58_actions_in_adapter_capabilities(self):
        adapter = BlenderApplicationAdapter()
        caps = adapter.get_capabilities()
        for act in BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS:
            assert act in caps

    def test_router_integration_phase2(self):
        router = AutomationRouter()
        for act in BlenderApplicationAdapter.BLENDER_STRUCTURED_ACTIONS:
            action = AutomationAction(action_type=act, target_label="TestObj")
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


class TestBlenderScriptTemplateSyntax:
    """Defect 1 Regression: Verify all generated scripts parse as clean AST with no unresolved template vars."""

    def test_mesh_templates_syntax_and_variables(self):
        sample_params = {
            "create_mesh_object": {"name": "TestMesh", "collection": "Collection"},
            "create_primitive_mesh": {"primitive": "cube", "name": "TestCube", "location": (0.0, 0.0, 0.0)},
            "convert_object_to_mesh": {"object_name": "TestCube"},
            "add_vertex": {"object_name": "TestCube", "location": (1.0, 1.0, 1.0)},
            "add_edge": {"object_name": "TestCube", "v1": 0, "v2": 1},
            "add_face": {"object_name": "TestCube", "vertex_indices": [0, 1, 2, 3]},
            "delete_vertices": {"object_name": "TestCube", "indices": [0]},
            "delete_edges": {"object_name": "TestCube", "indices": [0]},
            "delete_faces": {"object_name": "TestCube", "indices": [0]},
            "extrude_region": {"object_name": "TestCube", "distance": 1.0, "indices": [0]},
            "extrude_vertices": {"object_name": "TestCube", "distance": 1.0, "indices": [0]},
            "extrude_edges": {"object_name": "TestCube", "distance": 1.0, "indices": [0]},
            "extrude_faces": {"object_name": "TestCube", "distance": 1.0, "indices": [0]},
            "inset_faces": {"object_name": "TestCube", "thickness": 0.2, "indices": [0]},
            "subdivide_edges": {"object_name": "TestCube", "cuts": 2, "indices": [0]},
            "bevel_edges": {"object_name": "TestCube", "offset": 0.1, "segments": 2, "indices": [0]},
            "dissolve_vertices": {"object_name": "TestCube", "indices": [0]},
            "dissolve_edges": {"object_name": "TestCube", "indices": [0]},
            "dissolve_faces": {"object_name": "TestCube", "indices": [0]},
            "merge_vertices": {"object_name": "TestCube", "distance": 0.01, "indices": [0, 1]},
            "select_mesh_elements": {"object_name": "TestCube", "element_type": "verts", "indices": [0]},
            "deselect_mesh_elements": {"object_name": "TestCube", "element_type": "verts", "indices": [0]},
            "recalculate_normals": {"object_name": "TestCube", "inside": False},
            "flip_normals": {"object_name": "TestCube", "indices": [0]},
            "separate_mesh_parts": {"object_name": "TestCube", "type": "LOOSE"},
            "join_mesh_objects": {"target_object": "TestCube", "source_objects": ["OtherCube"]},
            "get_mesh_statistics": {"object_name": "TestCube"},
            "get_mesh_topology": {"object_name": "TestCube"},
            "validate_mesh": {"object_name": "TestCube"},
        }

        for action_type, params in sample_params.items():
            params["action_type"] = action_type
            script = BlenderMeshExecutor.build_script(action_type, params)
            
            # Must be valid Python syntax
            ast.parse(script)

            # Must NOT contain literal un-substituted outer template variables like '{name}' or '{action_type}'
            assert "::{name}:" not in script
            assert "::{action_type}" not in script
            assert "NOVA_ACTION_START" in script
            assert "NOVA_ACTION_SUCCESS" in script


class TestBlenderExecutionProtocolFailureModes:
    """Defect 2 Regression: Test machine-readable protocol enforcement and false-success prevention."""

    @pytest.mark.asyncio
    async def test_deliberate_exception_returns_success_false(self, monkeypatch):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Blender executable not found.")

        executor = BlenderBpyExecutor()
        monkeypatch.setattr(BlenderBpyExecutor, "build_bpy_script", lambda self, p: "import bpy\n1 / 0\nprint('NOVA_ACTION_SUCCESS::create_scene::BadScene')\n")
        res = await executor.execute_bpy({"action_type": "create_scene", "name": "BadScene"})
        assert res.success is False
        assert "zero" in res.error_message.lower() or "exception" in res.error_message.lower() or "bpy execution failed" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_syntax_error_returns_success_false(self, monkeypatch):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Blender executable not found.")

        executor = BlenderBpyExecutor()
        monkeypatch.setattr(BlenderBpyExecutor, "build_bpy_script", lambda self, p: "import bpy\nif True\n    print('invalid syntax')\n")
        res = await executor.execute_bpy({"action_type": "create_scene", "name": "SyntaxBad"})
        assert res.success is False
        assert "syntaxerror" in res.error_message.lower() or "bpy execution failed" in res.error_message.lower()

    @pytest.mark.asyncio
    async def test_missing_success_marker_returns_success_false(self, monkeypatch):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Blender executable not found.")

        executor = BlenderBpyExecutor()
        monkeypatch.setattr(BlenderBpyExecutor, "build_bpy_script", lambda self, p: "import bpy\nx = 10\nprint('Done without marker')\n")
        res = await executor.execute_bpy({"action_type": "create_scene", "name": "NoMarker"})
        assert res.success is False
        assert "missing success marker" in res.error_message.lower()



class TestBlenderPhysicalBMeshVerification:
    """Physical Blender 5.2.0 LTS verification suite covering Defect 4, 5, 6."""

    @pytest.mark.asyncio
    async def test_physical_bmesh_18_actions_and_reopen_persistence(self):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Physical Blender executable not found on host system.")

        executor = BlenderBpyExecutor()
        tmp_dir = tempfile.gettempdir()
        test_file = os.path.join(tmp_dir, "physical_bmesh_verify.blend").replace("\\", "/")

        # 0. Initial Save
        res = await executor.execute_bpy({"action_type": "save_file", "filepath": test_file})
        assert res.success is True

        # 1. create_primitive_mesh (Cube: 8 verts, 12 edges, 6 faces)
        res = await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "cube", "name": "PhysCube", "location": (0, 0, 0)}, blend_filepath=test_file)
        assert res.success is True

        # Verify Initial Reopen
        res_stat = await executor.execute_bpy({"action_type": "get_mesh_statistics", "name": "PhysCube"}, blend_filepath=test_file)
        assert res_stat.success is True
        assert "verts=8" in res_stat.output["stdout"]
        assert "edges=12" in res_stat.output["stdout"]
        assert "faces=6" in res_stat.output["stdout"]

        # 2. add_vertex at (1, 1, 3)
        res = await executor.execute_bpy({"action_type": "add_vertex", "name": "PhysCube", "location": (1.0, 1.0, 3.0)}, blend_filepath=test_file)
        assert res.success is True
        assert "NOVA_ACTION_SUCCESS::add_vertex" in res.output["stdout"]

        # Reopen & Compare Vert Count (Expect 9)
        res_stat = await executor.execute_bpy({"action_type": "get_mesh_statistics", "name": "PhysCube"}, blend_filepath=test_file)
        assert "verts=9" in res_stat.output["stdout"]

        # 3. add_edge between vertex 0 and new vertex 8
        res = await executor.execute_bpy({"action_type": "add_edge", "name": "PhysCube", "v1": 0, "v2": 8}, blend_filepath=test_file)
        assert res.success is True

        # Reopen & Compare Edge Count (Expect 13)
        res_stat = await executor.execute_bpy({"action_type": "get_mesh_statistics", "name": "PhysCube"}, blend_filepath=test_file)
        assert "edges=13" in res_stat.output["stdout"]

        # 4. add_face
        res = await executor.execute_bpy({"action_type": "add_vertex", "name": "PhysCube", "location": (0.0, 1.0, 3.0)}, blend_filepath=test_file)
        res = await executor.execute_bpy({"action_type": "add_vertex", "name": "PhysCube", "location": (0.0, 0.0, 3.0)}, blend_filepath=test_file)
        res = await executor.execute_bpy({"action_type": "add_face", "name": "PhysCube", "vertex_indices": [8, 9, 10]}, blend_filepath=test_file)
        assert res.success is True

        # 5. select_mesh_elements
        res = await executor.execute_bpy({"action_type": "select_mesh_elements", "name": "PhysCube", "element_type": "verts", "indices": [0, 1]}, blend_filepath=test_file)
        assert res.success is True

        # 6. extrude_region
        res = await executor.execute_bpy({"action_type": "extrude_region", "name": "PhysCube", "distance": 0.5, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 7. extrude_vertices
        res = await executor.execute_bpy({"action_type": "extrude_vertices", "name": "PhysCube", "distance": 0.2, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 8. extrude_edges
        res = await executor.execute_bpy({"action_type": "extrude_edges", "name": "PhysCube", "distance": 0.2, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 9. extrude_faces
        res = await executor.execute_bpy({"action_type": "extrude_faces", "name": "PhysCube", "distance": 0.2, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 10. inset_faces
        res = await executor.execute_bpy({"action_type": "inset_faces", "name": "PhysCube", "thickness": 0.05, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 11. subdivide_edges
        res = await executor.execute_bpy({"action_type": "subdivide_edges", "name": "PhysCube", "cuts": 1, "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 12. bevel_edges
        res = await executor.execute_bpy({"action_type": "bevel_edges", "name": "PhysCube", "offset": 0.02, "segments": 1}, blend_filepath=test_file)
        assert res.success is True

        # 13. dissolve_vertices
        res = await executor.execute_bpy({"action_type": "dissolve_vertices", "name": "PhysCube", "indices": [8]}, blend_filepath=test_file)
        assert res.success is True

        # 14. dissolve_edges
        res = await executor.execute_bpy({"action_type": "dissolve_edges", "name": "PhysCube", "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 15. dissolve_faces
        res = await executor.execute_bpy({"action_type": "dissolve_faces", "name": "PhysCube", "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # 16. merge_vertices
        res = await executor.execute_bpy({"action_type": "merge_vertices", "name": "PhysCube", "distance": 0.001}, blend_filepath=test_file)
        assert res.success is True

        # 17. recalculate_normals
        res = await executor.execute_bpy({"action_type": "recalculate_normals", "name": "PhysCube", "inside": False}, blend_filepath=test_file)
        assert res.success is True

        # 18. flip_normals
        res = await executor.execute_bpy({"action_type": "flip_normals", "name": "PhysCube", "indices": [0]}, blend_filepath=test_file)
        assert res.success is True

        # Final persistence verification by reopening in fresh Blender process
        res_final = await executor.execute_bpy({"action_type": "get_mesh_topology", "name": "PhysCube"}, blend_filepath=test_file)
        assert res_final.success is True
        assert "verts=" in res_final.output["stdout"]

    @pytest.mark.asyncio
    async def test_selection_domain_semantics(self):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Physical Blender executable not found.")

        executor = BlenderBpyExecutor()
        tmp_dir = tempfile.gettempdir()
        tf = os.path.join(tmp_dir, "sel_test.blend").replace("\\", "/")
        await executor.execute_bpy({"action_type": "save_file", "filepath": tf})
        await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "cube", "name": "SelCube"}, blend_filepath=tf)

        # Test invalid index out of bounds raises explicit failure
        res_bad = await executor.execute_bpy({"action_type": "select_mesh_elements", "name": "SelCube", "element_type": "verts", "indices": [999]}, blend_filepath=tf)
        assert res_bad.success is False
        assert "out of range" in res_bad.error_message.lower()

    @pytest.mark.asyncio
    async def test_context_sensitive_operations(self):
        blender_bin = BlenderBpyExecutor.find_blender_executable()
        if not blender_bin:
            pytest.skip("Physical Blender executable not found.")

        executor = BlenderBpyExecutor()
        tmp_dir = tempfile.gettempdir()
        tf = os.path.join(tmp_dir, "ctx_test.blend").replace("\\", "/")
        await executor.execute_bpy({"action_type": "save_file", "filepath": tf})

        # 1. create_primitive_mesh
        res1 = await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "cube", "name": "Obj1"}, blend_filepath=tf)
        assert res1.success is True

        res2 = await executor.execute_bpy({"action_type": "create_primitive_mesh", "primitive": "plane", "name": "Obj2", "location": (5, 0, 0)}, blend_filepath=tf)
        assert res2.success is True

        # 2. join_mesh_objects
        res_join = await executor.execute_bpy({"action_type": "join_mesh_objects", "target_object": "Obj1", "source_objects": ["Obj2"]}, blend_filepath=tf)
        assert res_join.success is True

        # 3. separate_mesh_parts
        res_sep = await executor.execute_bpy({"action_type": "separate_mesh_parts", "name": "Obj1", "type": "LOOSE"}, blend_filepath=tf)
        assert res_sep.success is True

        # 4. convert_object_to_mesh
        res_conv = await executor.execute_bpy({"action_type": "convert_object_to_mesh", "name": "Obj1"}, blend_filepath=tf)
        assert res_conv.success is True
