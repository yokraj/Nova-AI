"""Blender Scene & Collection Domain Executor.

Handles template BPY script generation for:
- create_scene, delete_scene, rename_scene, set_scene_units
- create_collection, delete_collection, rename_collection
- link_object_to_collection, unlink_object_from_collection
"""

from typing import Any, Dict


class BlenderSceneExecutor:
    """Constructs BPY scripts for Blender Scene and Collection hierarchy actions."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Returns validated BPY script string for specified scene/collection action."""
        if action_type == "create_scene":
            name = params.get("name", "Scene")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"scene = bpy.data.scenes.new(name='{name}')\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "delete_scene":
            name = params.get("name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                "if len(bpy.data.scenes) <= 1:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Cannot delete sole remaining scene.')\n"
                "else:\n"
                f"    sc = bpy.data.scenes.get('{name}')\n"
                "    if sc:\n"
                "        bpy.data.scenes.remove(sc, do_unlink=True)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Scene {name} not found.')\n"
            )

        elif action_type == "rename_scene":
            name = params.get("name", "")
            new_name = params.get("new_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"sc = bpy.data.scenes.get('{name}')\n"
                "if sc:\n"
                f"    sc.name = '{new_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{new_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Scene {name} not found.')\n"
            )

        elif action_type == "set_scene_units":
            system = params.get("system", "METRIC")
            scale = params.get("scale_length", 1.0)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                "sc = bpy.context.scene\n"
                f"sc.unit_settings.system = '{system}'\n"
                f"sc.unit_settings.scale_length = {scale}\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{system}:{scale}')\n"
            )

        elif action_type == "create_collection":
            name = params.get("name", "Collection")
            parent = params.get("parent_collection")
            if parent:
                link_code = (
                    f"pcol = bpy.data.collections.get('{parent}') or bpy.context.scene.collection\n"
                    "pcol.children.link(col)\n"
                )
            else:
                link_code = "bpy.context.scene.collection.children.link(col)\n"

            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"col = bpy.data.collections.new(name='{name}')\n"
                + link_code +
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "delete_collection":
            name = params.get("name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"col = bpy.data.collections.get('{name}')\n"
                "if col:\n"
                "    bpy.data.collections.remove(col)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Collection {name} not found.')\n"
            )

        elif action_type == "rename_collection":
            name = params.get("name", "")
            new_name = params.get("new_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"col = bpy.data.collections.get('{name}')\n"
                "if col:\n"
                f"    col.name = '{new_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{new_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Collection {name} not found.')\n"
            )

        elif action_type == "link_object_to_collection":
            obj_name = params.get("object_name", "")
            col_name = params.get("collection_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                f"col = bpy.data.collections.get('{col_name}')\n"
                "if obj and col:\n"
                "    if obj.name not in col.objects:\n"
                "        col.objects.link(obj)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{col_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object or Collection not found.')\n"
            )

        elif action_type == "unlink_object_from_collection":
            obj_name = params.get("object_name", "")
            col_name = params.get("collection_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                f"col = bpy.data.collections.get('{col_name}')\n"
                "if obj and col:\n"
                "    if obj.name in col.objects:\n"
                "        col.objects.unlink(obj)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{col_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object or Collection not found.')\n"
            )

        raise ValueError(f"Action '{action_type}' not supported by BlenderSceneExecutor.")

