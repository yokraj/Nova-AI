"""Blender Modifier Stack & Non-Destructive Modeling Domain Executor.

Handles template BPY script generation for 10 modifier actions:
- add_modifier, remove_modifier, rename_modifier, move_modifier
- get_modifiers, get_modifier_state, set_modifier_properties
- set_modifier_viewport_visibility, set_modifier_render_visibility
- apply_modifier

Supported Modifier Types:
- SUBSURF, MIRROR, BEVEL, SOLIDIFY, ARRAY, BOOLEAN, DECIMATE, WELD, WEIGHTED_NORMAL
"""

from typing import Any, Dict, List, Optional


class BlenderModifierExecutor:
    """Constructs BPY script templates for Blender modifier stack operations."""

    ALLOWED_MODIFIERS = {
        "SUBSURF",
        "MIRROR",
        "BEVEL",
        "SOLIDIFY",
        "ARRAY",
        "BOOLEAN",
        "DECIMATE",
        "WELD",
        "WEIGHTED_NORMAL",
    }


    SUBDIVISION_TYPES = {"CATMULL_CLARK", "SIMPLE"}
    BEVEL_LIMIT_METHODS = {"NONE", "ANGLE", "WEIGHT", "VGROUP"}
    BEVEL_AFFECTS = {"VERTICES", "EDGES"}
    BOOLEAN_OPERATIONS = {"DIFFERENCE", "UNION", "INTERSECT"}
    BOOLEAN_SOLVERS = {"FAST", "EXACT"}
    DECIMATE_TYPES = {"COLLAPSE", "UNSUBDIV", "DISSOLVE"}
    WELD_MODES = {"ALL", "CONNECTED"}

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Returns validated BPY script string for specified modifier action."""
        name = params.get("object_name") or params.get("name", "")

        if action_type == "add_modifier":
            mod_type = str(params.get("modifier_type") or params.get("type", "SUBSURF")).upper()
            if mod_type not in cls.ALLOWED_MODIFIERS:
                mod_type = "SUBSURF"
            mod_name = params.get("modifier_name") or params.get("mod_name") or mod_type.title()

            props_code = cls._build_property_assignment_code(mod_type, params)

            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}') or obj.modifiers.new(name='{mod_name}', type='{mod_type}')\n"
                "    if mod:\n"
                + props_code +
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}:{mod_type}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "remove_modifier":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                "        obj.modifiers.remove(mod)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "rename_modifier":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            new_name = params.get("new_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                f"        mod.name = '{new_name}'\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{new_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "move_modifier":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            direction = str(params.get("direction", "up")).lower()
            to_idx = params.get("index") if "index" in params else params.get("to_index")

            if to_idx is not None:
                move_code = f"bpy.ops.object.modifier_move_to_index(modifier='{mod_name}', index={int(to_idx)})"
            elif direction in ("down", "move_down"):
                move_code = f"bpy.ops.object.modifier_move_down(modifier='{mod_name}')"
            else:
                move_code = f"bpy.ops.object.modifier_move_up(modifier='{mod_name}')"

            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                "        bpy.ops.object.select_all(action='DESELECT')\n"
                "        obj.select_set(True)\n"
                "        bpy.context.view_layer.objects.active = obj\n"
                f"        {move_code}\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "get_modifiers":
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    mods = [{'name': m.name, 'type': m.type, 'show_viewport': m.show_viewport, 'show_render': m.show_render} for m in obj.modifiers]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:count={{len(mods)}}:mods={{mods}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "get_modifier_state":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                f"        print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}:type={{mod.type}}:vp={{mod.show_viewport}}:render={{mod.show_render}}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "set_modifier_properties":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            mod_type = str(params.get("modifier_type") or params.get("type", "")).upper()
            props_code = cls._build_property_assignment_code(mod_type, params)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                + props_code +
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type in ("set_modifier_viewport_visibility", "set_modifier_render_visibility"):
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            visible = bool(params.get("show_viewport", params.get("show_render", params.get("visible", True))))
            attr = "show_viewport" if action_type == "set_modifier_viewport_visibility" else "show_render"
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                f"        mod.{attr} = {visible}\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}:{visible}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "apply_modifier":
            mod_name = params.get("modifier_name") or params.get("mod_name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                "        bpy.ops.object.select_all(action='DESELECT')\n"
                "        obj.select_set(True)\n"
                "        bpy.context.view_layer.objects.active = obj\n"
                f"        bpy.ops.object.modifier_apply(modifier='{mod_name}')\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{mod_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Modifier {mod_name} not found on {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        raise ValueError(f"Action '{action_type}' not supported by BlenderModifierExecutor.")

    @classmethod
    def _build_property_assignment_code(cls, mod_type: str, params: Dict[str, Any]) -> str:
        """Constructs type-checked Python assignment code for modifier properties."""
        p = dict(params)
        if "properties" in params and isinstance(params["properties"], dict):
            p.update(params["properties"])
        params = p

        lines = []

        # SUBSURF
        if any(k in params for k in ("levels", "render_levels", "subdivision_type")):
            lines.append("        if mod.type == 'SUBSURF':\n")
            if "levels" in params:
                lvl = max(0, min(6, int(params["levels"])))
                lines.append(f"            mod.levels = {lvl}\n")
            if "render_levels" in params:
                rlvl = max(0, min(6, int(params["render_levels"])))
                lines.append(f"            mod.render_levels = {rlvl}\n")
            if "subdivision_type" in params:
                stype = str(params["subdivision_type"]).upper()
                if stype in cls.SUBDIVISION_TYPES:
                    lines.append(f"            mod.subdivision_type = '{stype}'\n")

        # MIRROR
        if any(k in params for k in ("use_axis_x", "use_axis_y", "use_axis_z", "use_clip", "use_mirror_merge", "merge_threshold")):
            lines.append("        if mod.type == 'MIRROR':\n")
            for idx, axis in enumerate(("x", "y", "z")):
                key = f"use_axis_{axis}"
                if key in params:
                    lines.append(f"            mod.use_axis[{idx}] = {bool(params[key])}\n")
            if "use_clip" in params:
                lines.append(f"            mod.use_clip = {bool(params['use_clip'])}\n")
            if "use_mirror_merge" in params:
                lines.append(f"            mod.use_mirror_merge = {bool(params['use_mirror_merge'])}\n")
            if "merge_threshold" in params:
                lines.append(f"            mod.merge_threshold = {max(0.0, float(params['merge_threshold']))}\n")

        # BEVEL
        if any(k in params for k in ("width", "offset", "segments", "limit_method", "angle_limit", "affect")):
            lines.append("        if mod.type == 'BEVEL':\n")
            if "width" in params or "offset" in params:
                w = max(0.0, float(params.get("width", params.get("offset", 0.1))))
                lines.append(f"            mod.width = {w}\n")
            if "segments" in params:
                seg = max(1, int(params["segments"]))
                lines.append(f"            mod.segments = {seg}\n")
            if "limit_method" in params:
                lm = str(params["limit_method"]).upper()
                if lm in cls.BEVEL_LIMIT_METHODS:
                    lines.append(f"            mod.limit_method = '{lm}'\n")
            if "angle_limit" in params:
                lines.append(f"            mod.angle_limit = {float(params['angle_limit'])}\n")
            if "affect" in params:
                aff = str(params["affect"]).upper()
                if aff in cls.BEVEL_AFFECTS:
                    lines.append(f"            mod.affect = '{aff}'\n")

        # SOLIDIFY
        if any(k in params for k in ("thickness", "offset", "use_rim", "use_rim_only")):
            lines.append("        if mod.type == 'SOLIDIFY':\n")
            if "thickness" in params:
                lines.append(f"            mod.thickness = {float(params['thickness'])}\n")
            if "offset" in params:
                lines.append(f"            mod.offset = {float(params['offset'])}\n")
            if "use_rim" in params:
                lines.append(f"            mod.use_rim = {bool(params['use_rim'])}\n")
            if "use_rim_only" in params:
                lines.append(f"            mod.use_rim_only = {bool(params['use_rim_only'])}\n")

        # ARRAY
        if any(k in params for k in ("count", "relative_offset", "constant_offset", "merge_vertices", "merge_threshold", "object_offset")):
            lines.append("        if mod.type == 'ARRAY':\n")
            if "count" in params:
                cnt = max(1, int(params["count"]))
                lines.append(f"            mod.count = {cnt}\n")
            if "relative_offset" in params and isinstance(params["relative_offset"], (list, tuple)) and len(params["relative_offset"]) >= 3:
                rx, ry, rz = float(params["relative_offset"][0]), float(params["relative_offset"][1]), float(params["relative_offset"][2])
                lines.append(f"            mod.use_relative_offset = True\n            mod.relative_offset_displace = ({rx}, {ry}, {rz})\n")
            if "constant_offset" in params and isinstance(params["constant_offset"], (list, tuple)) and len(params["constant_offset"]) >= 3:
                cx, cy, cz = float(params["constant_offset"][0]), float(params["constant_offset"][1]), float(params["constant_offset"][2])
                lines.append(f"            mod.use_constant_offset = True\n            mod.constant_offset_displace = ({cx}, {cy}, {cz})\n")
            if "merge_vertices" in params:
                lines.append(f"            mod.use_merge_vertices = {bool(params['merge_vertices'])}\n")
            if "merge_threshold" in params:
                lines.append(f"            mod.merge_threshold = {max(0.0, float(params['merge_threshold']))}\n")
            if "object_offset" in params:
                off_obj = str(params["object_offset"])
                lines.append(f"            off_target = bpy.data.objects.get('{off_obj}')\n            if off_target:\n                mod.offset_object = off_target\n                mod.use_object_offset = True\n")

        # BOOLEAN
        if any(k in params for k in ("operand_object", "object", "operation", "solver")):
            lines.append("        if mod.type == 'BOOLEAN':\n")
            if "operation" in params:
                op = str(params["operation"]).upper()
                if op in cls.BOOLEAN_OPERATIONS:
                    lines.append(f"            mod.operation = '{op}'\n")
            if "solver" in params:
                sol = str(params["solver"]).upper()
                if sol in cls.BOOLEAN_SOLVERS:
                    lines.append(f"            mod.solver = '{sol}'\n")
            operand = params.get("operand_object") or params.get("object")
            target_name = params.get("object_name") or params.get("name", "")
            if operand:
                if str(operand) == str(target_name):
                    lines.append(f"            print('NOVA_ACTION_ERROR::add_modifier::Self-referencing boolean operand is invalid.')\n")
                else:
                    lines.append(f"            operand_obj = bpy.data.objects.get('{operand}')\n            if operand_obj:\n                mod.object = operand_obj\n            else:\n                print('NOVA_ACTION_ERROR::add_modifier::Operand object {operand} not found.')\n")

        # DECIMATE
        if any(k in params for k in ("ratio", "iterations", "angle_limit", "decimate_type")):
            lines.append("        if mod.type == 'DECIMATE':\n")
            if "ratio" in params:
                rat = max(0.0, min(1.0, float(params["ratio"])))
                lines.append(f"            mod.ratio = {rat}\n")
            if "iterations" in params:
                it = max(1, int(params["iterations"]))
                lines.append(f"            mod.iterations = {it}\n")
            if "angle_limit" in params:
                lines.append(f"            mod.angle_limit = {float(params['angle_limit'])}\n")
            if "decimate_type" in params or "mode" in params:
                dt = str(params.get("decimate_type", params.get("mode"))).upper()
                if dt in cls.DECIMATE_TYPES:
                    lines.append(f"            mod.decimate_type = '{dt}'\n")

        # WELD
        if ("merge_threshold" in params or "mode" in params or "distance" in params):
            lines.append("        if mod.type == 'WELD':\n")
            if "merge_threshold" in params or "distance" in params:
                dist = max(0.0, float(params.get("merge_threshold", params.get("distance", 0.001))))
                lines.append(f"            mod.merge_threshold = {dist}\n")
            if "mode" in params:
                wm = str(params["mode"]).upper()
                if wm in cls.WELD_MODES:
                    lines.append(f"            mod.mode = '{wm}'\n")

        # WEIGHTED_NORMAL
        if any(k in params for k in ("keep_sharp", "weight", "threshold")):
            lines.append("        if mod.type == 'WEIGHTED_NORMAL':\n")
            if "keep_sharp" in params:
                lines.append(f"            mod.keep_sharp = {bool(params['keep_sharp'])}\n")
            if "weight" in params:
                w = max(1, min(100, int(params["weight"])))
                lines.append(f"            mod.weight = {w}\n")
            if "threshold" in params:
                lines.append(f"            mod.threshold = {max(0.0, float(params['threshold']))}\n")

        if not lines:
            return "        pass\n"
        return "".join(lines)


SUPPORTED_MODIFIER_TYPES = BlenderModifierExecutor.ALLOWED_MODIFIERS

VALID_MODIFIER_PROPERTIES = {
    "SUBSURF": {"levels", "render_levels", "subdivision_type"},
    "MIRROR": {"use_axis_x", "use_axis_y", "use_axis_z", "use_clip", "use_mirror_merge", "merge_threshold"},
    "BEVEL": {"width", "offset", "segments", "limit_method", "angle_limit", "affect"},
    "SOLIDIFY": {"thickness", "offset", "use_rim", "use_rim_only"},
    "ARRAY": {"count", "relative_offset", "constant_offset", "merge_vertices", "merge_threshold", "object_offset"},
    "BOOLEAN": {"operation", "solver", "operand_object"},
    "DECIMATE": {"ratio", "iterations", "angle_limit", "decimate_type"},
    "WELD": {"merge_threshold", "mode"},
    "WEIGHTED_NORMAL": {"keep_sharp", "weight", "threshold"},
}

