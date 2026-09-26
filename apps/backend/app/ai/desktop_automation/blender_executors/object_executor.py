"""Blender Object Hierarchy Domain Executor.

Handles template BPY script generation for:
- duplicate_object, hide_object, show_object, apply_transform
- parent_object, unparent_object, add_constraint, remove_constraint
"""

from typing import Any, Dict


class BlenderObjectExecutor:
    """Constructs BPY scripts for Blender object operations, transforms, parenting, and constraints."""

    ALLOWED_CONSTRAINTS = {
        "COPY_LOCATION",
        "COPY_ROTATION",
        "COPY_SCALE",
        "TRACK_TO",
        "LIMIT_LOCATION",
        "LIMIT_ROTATION",
        "CHILD_OF",
        "DAMPED_TRACK",
    }

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Returns validated BPY script string for specified object action."""
        if action_type == "duplicate_object":
            source = params.get("source_object") or params.get("name", "")
            new_name = params.get("new_name")
            new_name_code = f"    dup.name = '{new_name}'\n" if new_name else ""
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"src = bpy.data.objects.get('{source}')\n"
                "if src:\n"
                "    dup = src.copy()\n"
                "    if src.data:\n"
                "        dup.data = src.data.copy()\n"
                + new_name_code +
                "    col = bpy.context.collection or bpy.context.scene.collection\n"
                "    col.objects.link(dup)\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{source}:{{dup.name}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Source object {source} not found.')\n"
            )

        elif action_type == "hide_object":
            name = params.get("object_name") or params.get("name", "")
            hide_vp = params.get("hide_viewport", True)
            hide_ren = params.get("hide_render", True)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    obj.hide_viewport = {hide_vp}\n"
                f"    obj.hide_render = {hide_ren}\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "show_object":
            name = params.get("object_name") or params.get("name", "")
            show_vp = params.get("show_viewport", True)
            show_ren = params.get("show_render", True)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    obj.hide_viewport = {not show_vp}\n"
                f"    obj.hide_render = {not show_ren}\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "apply_transform":
            name = params.get("object_name") or params.get("name", "")
            loc = params.get("location", True)
            rot = params.get("rotation", True)
            scl = params.get("scale", True)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                f"    bpy.ops.object.transform_apply(location={loc}, rotation={rot}, scale={scl})\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "parent_object":
            child = params.get("child", "")
            parent = params.get("parent", "")
            keep_trans = params.get("keep_transform", True)
            keep_code = "    c.matrix_parent_inverse = p.matrix_world.inverted()\n" if keep_trans else ""
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"c = bpy.data.objects.get('{child}')\n"
                f"p = bpy.data.objects.get('{parent}')\n"
                "if c and p:\n"
                "    c.parent = p\n"
                + keep_code +
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{child}:{parent}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Child or parent object not found.')\n"
            )

        elif action_type == "unparent_object":
            child = params.get("child", "")
            keep_trans = params.get("keep_transform", True)
            trans_save = "    mat = c.matrix_world.copy()\n" if keep_trans else ""
            trans_restore = "    c.matrix_world = mat\n" if keep_trans else ""
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"c = bpy.data.objects.get('{child}')\n"
                "if c and c.parent:\n"
                + trans_save +
                "    c.parent = None\n"
                + trans_restore +
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{child}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Child object or parent relationship not found.')\n"
            )

        elif action_type == "add_constraint":
            name = params.get("object_name") or params.get("name", "")
            c_type = str(params.get("constraint_type", "COPY_LOCATION")).upper()
            target = params.get("target_object")
            c_name = params.get("constraint_name")

            if c_type not in cls.ALLOWED_CONSTRAINTS:
                c_type = "COPY_LOCATION"

            target_code = f"    tgt = bpy.data.objects.get('{target}')\n    if tgt:\n        con.target = tgt\n" if target else ""
            name_code = f"    con.name = '{c_name}'\n" if c_name else ""

            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    con = obj.constraints.new(type='{c_type}')\n"
                + target_code +
                name_code +
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{c_type}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "remove_constraint":
            name = params.get("object_name") or params.get("name", "")
            c_name = params.get("constraint_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    con = obj.constraints.get('{c_name}')\n"
                "    if con:\n"
                "        obj.constraints.remove(con)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{c_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Constraint {c_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        raise ValueError(f"Action '{action_type}' not supported by BlenderObjectExecutor.")

