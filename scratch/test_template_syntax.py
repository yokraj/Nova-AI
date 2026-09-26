import ast
import sys
import os

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath("apps/backend"))

from app.ai.desktop_automation.blender_executors.mesh_executor import BlenderMeshExecutor
from app.ai.desktop_automation.blender_executors.object_executor import BlenderObjectExecutor
from app.ai.desktop_automation.blender_executors.scene_executor import BlenderSceneExecutor
from app.ai.desktop_automation.blender_adapter import BlenderBpyExecutor

def test_all_templates():
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

    errors = []
    for action_type, params in sample_params.items():
        params["action_type"] = action_type
        script = BlenderMeshExecutor.build_script(action_type, params)
        try:
            ast.parse(script)
            print(f"[PASS] {action_type} AST parse clean.")
        except Exception as e:
            print(f"[FAIL] {action_type} AST parse failed: {e}")
            errors.append((action_type, str(e), script))

    print(f"\nTotal Tested: {len(sample_params)}, Failures: {len(errors)}")
    for act, err, scr in errors:
        print(f"\n--- {act} ---")
        print(err)
        print("Generated Code:")
        print(scr)

if __name__ == "__main__":
    test_all_templates()
