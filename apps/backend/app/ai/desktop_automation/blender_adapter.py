"""Blender BPY Action Validator and Controlled Execution Engine.

Enforces strict parameter validation and template-based BPY script generation.
NEVER executes raw or arbitrary AI-generated Python strings directly.
"""

from typing import Any, Dict, Optional, Tuple
import os
import re
import tempfile
import time
import subprocess
import structlog

from app.ai.desktop_automation.models import (
    AutomationAction,
    AutomationResult,
)
from app.ai.desktop_automation.blender_executors.scene_executor import BlenderSceneExecutor
from app.ai.desktop_automation.blender_executors.object_executor import BlenderObjectExecutor
from app.ai.desktop_automation.blender_executors.mesh_executor import BlenderMeshExecutor
from app.ai.desktop_automation.blender_executors.modifier_executor import BlenderModifierExecutor
from app.ai.desktop_automation.blender_executors.material_executor import BlenderMaterialExecutor, SUPPORTED_MATERIAL_ACTIONS
from app.ai.desktop_automation.blender_executors.camera_lighting_executor import BlenderCameraLightingExecutor, SUPPORTED_CAMERA_LIGHTING_ACTIONS
from app.ai.desktop_automation.blender_executors.animation_executor import BlenderAnimationExecutor, SUPPORTED_ANIMATION_ACTIONS
from app.ai.desktop_automation.blender_executors.render_executor import BlenderRenderExecutor, SUPPORTED_RENDER_ACTIONS
from app.ai.desktop_automation.blender_executors.geometry_nodes_executor import BlenderGeometryNodesExecutor, SUPPORTED_GEOMETRY_NODES_ACTIONS, ALLOWED_NODE_TYPES, ALLOWED_SOCKET_TYPES
from app.ai.desktop_automation.blender_executors.physics_executor import BlenderPhysicsExecutor, SUPPORTED_PHYSICS_ACTIONS, ALLOWED_COLLISION_SHAPES, ALLOWED_FORCE_FIELD_TYPES, ALLOWED_FLUID_TYPES
from app.ai.desktop_automation.blender_executors.asset_pipeline_executor import BlenderAssetPipelineExecutor, SUPPORTED_ASSET_PIPELINE_ACTIONS, ALLOWED_GLTF_FORMATS

logger = structlog.get_logger("blender_adapter")


class BlenderActionValidationError(Exception):
    """Raised when Blender action parameters fail validation."""

    pass


class BlenderActionValidator:
    """Validates Blender operation parameters against strict schemas before execution."""

    ALLOWED_PRIMITIVES = {"cube", "uv_sphere", "icosphere", "cylinder", "plane"}
    ALLOWED_LIGHT_TYPES = {"POINT", "SUN", "SPOT", "AREA"}
    ALLOWED_UNIT_SYSTEMS = {"NONE", "METRIC", "IMPERIAL"}

    FORBIDDEN_SCRIPT_KEYS = {
        "raw_python",
        "eval_python",
        "blender_bpy_script",
        "run_script",
        "exec",
        "eval",
        "script",
        "code",
    }

    SCENE_ACTIONS = {
        "create_scene",
        "delete_scene",
        "rename_scene",
        "set_scene_units",
        "create_collection",
        "delete_collection",
        "rename_collection",
        "link_object_to_collection",
        "unlink_object_from_collection",
    }

    OBJECT_HIERARCHY_ACTIONS = {
        "duplicate_object",
        "hide_object",
        "show_object",
        "apply_transform",
        "parent_object",
        "unparent_object",
        "add_constraint",
        "remove_constraint",
    }

    MESH_ACTIONS = {
        "create_mesh_object",
        "create_primitive_mesh",
        "convert_object_to_mesh",
        "add_vertex",
        "add_edge",
        "add_face",
        "delete_vertices",
        "delete_edges",
        "delete_faces",
        "extrude_region",
        "extrude_vertices",
        "extrude_edges",
        "extrude_faces",
        "inset_faces",
        "subdivide_edges",
        "bevel_edges",
        "dissolve_vertices",
        "dissolve_edges",
        "dissolve_faces",
        "merge_vertices",
        "select_mesh_elements",
        "deselect_mesh_elements",
        "recalculate_normals",
        "flip_normals",
        "separate_mesh_parts",
        "join_mesh_objects",
        "get_mesh_statistics",
        "get_mesh_topology",
        "validate_mesh",
    }

    MODIFIER_ACTIONS = {
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
    }

    MATERIAL_ACTIONS = SUPPORTED_MATERIAL_ACTIONS
    CAMERA_LIGHTING_ACTIONS = SUPPORTED_CAMERA_LIGHTING_ACTIONS
    ANIMATION_ACTIONS = SUPPORTED_ANIMATION_ACTIONS
    RENDER_ACTIONS = SUPPORTED_RENDER_ACTIONS
    GEOMETRY_NODES_ACTIONS = SUPPORTED_GEOMETRY_NODES_ACTIONS
    PHYSICS_ACTIONS = SUPPORTED_PHYSICS_ACTIONS
    ASSET_PIPELINE_ACTIONS = SUPPORTED_ASSET_PIPELINE_ACTIONS

    @classmethod
    def validate_action(cls, action: AutomationAction) -> Dict[str, Any]:
        """Validates action parameter schema and returns sanitized parameter dictionary."""
        action_type = action.action_type.lower().replace("blender:", "")

        # Reject any arbitrary code parameter attempts
        params_source = {}
        if isinstance(action.parameters, dict):
            params_source.update(action.parameters)
        if isinstance(action.value, dict):
            params_source.update(action.value)
        if action.selector:
            params_source.update(action.selector)

        for f_key in cls.FORBIDDEN_SCRIPT_KEYS:
            if f_key in params_source:
                raise BlenderActionValidationError(f"Arbitrary script parameter '{f_key}' is strictly forbidden.")

        if action_type in cls.ANIMATION_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type

            raw_name = params_source.get("object_name") or params_source.get("armature_name") or params_source.get("name") or action.target_label or "Object"
            res["name"] = cls.sanitize_name(raw_name)
            res["object_name"] = res["name"]

            for name_field in ("armature_name", "bone_name", "action_name", "new_name", "parent_bone", "track_name", "strip_name", "target_object", "constraint_name"):
                if name_field in params_source:
                    res[name_field] = cls.sanitize_name(str(params_source[name_field]))

            if "interpolation" in params_source:
                interp = str(params_source["interpolation"]).upper()
                if interp not in BlenderAnimationExecutor.ALLOWED_INTERPOLATION:
                    raise BlenderActionValidationError(f"Invalid interpolation '{interp}'. Allowed: {BlenderAnimationExecutor.ALLOWED_INTERPOLATION}")
                res["interpolation"] = interp

            if "easing" in params_source:
                eas = str(params_source["easing"]).upper()
                if eas not in BlenderAnimationExecutor.ALLOWED_EASING:
                    raise BlenderActionValidationError(f"Invalid easing '{eas}'. Allowed: {BlenderAnimationExecutor.ALLOWED_EASING}")
                res["easing"] = eas

            if "handle_type" in params_source:
                htype = str(params_source["handle_type"]).upper()
                if htype not in BlenderAnimationExecutor.ALLOWED_HANDLE_TYPES:
                    raise BlenderActionValidationError(f"Invalid handle_type '{htype}'. Allowed: {BlenderAnimationExecutor.ALLOWED_HANDLE_TYPES}")
                res["handle_type"] = htype

            if "extrapolation" in params_source:
                extrap = str(params_source["extrapolation"]).upper()
                if extrap not in BlenderAnimationExecutor.ALLOWED_EXTRAPOLATION:
                    raise BlenderActionValidationError(f"Invalid extrapolation '{extrap}'. Allowed: {BlenderAnimationExecutor.ALLOWED_EXTRAPOLATION}")
                res["extrapolation"] = extrap

            if "constraint_type" in params_source:
                ctype = str(params_source["constraint_type"]).upper()
                if ctype not in BlenderAnimationExecutor.ALLOWED_CONSTRAINT_TYPES:
                    raise BlenderActionValidationError(f"Invalid constraint_type '{ctype}'. Allowed: {BlenderAnimationExecutor.ALLOWED_CONSTRAINT_TYPES}")
                res["constraint_type"] = ctype

            if "data_path" in params_source:
                dp = str(params_source["data_path"]).strip()
                if any(f in dp for f in (";", "'", '"', "import", "exec", "eval", "os.")):
                    raise BlenderActionValidationError(f"Unsafe data_path '{dp}' forbidden.")
                res["data_path"] = dp

            for vec_field in ("location", "rotation", "scale", "head", "tail"):
                if vec_field in params_source and isinstance(params_source[vec_field], (list, tuple)):
                    res[vec_field] = cls.validate_vector3(params_source[vec_field])

            return res


        if action_type in cls.MATERIAL_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type
            raw_mat_name = params_source.get("material_name") or params_source.get("name") or action.target_label or "Material"
            res["material_name"] = cls.sanitize_name(raw_mat_name)
            res["name"] = res["material_name"]

            if "object_name" in params_source or "target_label" in params_source or action.target_label:
                res["object_name"] = cls.sanitize_name(params_source.get("object_name") or params_source.get("target_label") or action.target_label or "Cube")
                res["target_label"] = res["object_name"]

            if "image_path" in params_source:
                img_p = str(params_source["image_path"])
                if not os.path.exists(img_p):
                    raise BlenderActionValidationError(f"Image texture path '{img_p}' does not exist.")
                res["image_path"] = img_p

            if "node_type" in params_source:
                ntype = str(params_source["node_type"])
                if ntype not in BlenderMaterialExecutor.ALLOWED_NODE_TYPES:
                    raise BlenderActionValidationError(f"Node type '{ntype}' is not in allowed node types.")
                res["node_type"] = ntype

            return res

        if action_type in cls.CAMERA_LIGHTING_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type
            
            raw_cam_name = params_source.get("camera_name") or params_source.get("light_name") or params_source.get("name") or action.target_label or "CameraOrLight"
            res["camera_name"] = cls.sanitize_name(raw_cam_name)
            res["light_name"] = res["camera_name"]
            res["name"] = res["camera_name"]

            if "new_name" in params_source:
                res["new_name"] = cls.sanitize_name(str(params_source["new_name"]))

            if "target_object" in params_source or "target" in params_source:
                res["target_object"] = cls.sanitize_name(str(params_source.get("target_object") or params_source.get("target")))

            if "camera_type" in params_source:
                ctype = str(params_source["camera_type"]).upper()
                if ctype not in BlenderCameraLightingExecutor.ALLOWED_CAMERA_TYPES:
                    raise BlenderActionValidationError(f"Invalid camera_type '{ctype}'. Allowed: {BlenderCameraLightingExecutor.ALLOWED_CAMERA_TYPES}")
                res["camera_type"] = ctype

            if "light_type" in params_source:
                ltype = str(params_source["light_type"]).upper()
                if ltype not in BlenderCameraLightingExecutor.ALLOWED_LIGHT_TYPES:
                    raise BlenderActionValidationError(f"Invalid light_type '{ltype}'. Allowed: {BlenderCameraLightingExecutor.ALLOWED_LIGHT_TYPES}")
                res["light_type"] = ltype

            for v_key in ("location", "rotation", "scale", "delta", "color", "target_location"):
                if v_key in params_source and isinstance(params_source[v_key], (list, tuple)):
                    res[v_key] = cls.validate_vector3(params_source[v_key])

            if "lens" in params_source:
                try:
                    lens = float(params_source["lens"])
                    if lens <= 0.0:
                        raise BlenderActionValidationError(f"Lens focal length must be > 0, got {lens}")
                    res["lens"] = lens
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid float for lens focal length.")

            if "energy" in params_source:
                try:
                    energy = float(params_source["energy"])
                    if energy < 0.0:
                        raise BlenderActionValidationError(f"Light energy must be >= 0, got {energy}")
                    res["energy"] = energy
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid float for light energy.")

            if "temperature" in params_source:
                try:
                    temp = float(params_source["temperature"])
                    if temp < 1000.0 or temp > 12000.0:
                        raise BlenderActionValidationError(f"Kelvin temperature {temp} out of valid range [1000.0, 12000.0]")
                    res["temperature"] = temp
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid float for light temperature.")

            return res

        if action_type in cls.RENDER_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type

            for path_key in ("filepath", "output_path"):
                if path_key in params_source and params_source[path_key]:
                    p_val = str(params_source[path_key])
                    if ".." in p_val or p_val.startswith("\\\\"):
                        raise BlenderActionValidationError(f"Path traversal or network path forbidden in '{path_key}': {p_val}")
                    res[path_key] = p_val.replace("\\", "/")

            if "resolution_x" in params_source:
                try:
                    rx = int(params_source["resolution_x"])
                    if rx <= 0:
                        raise BlenderActionValidationError(f"resolution_x must be > 0, got {rx}")
                    res["resolution_x"] = rx
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid integer for resolution_x.")

            if "resolution_y" in params_source:
                try:
                    ry = int(params_source["resolution_y"])
                    if ry <= 0:
                        raise BlenderActionValidationError(f"resolution_y must be > 0, got {ry}")
                    res["resolution_y"] = ry
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid integer for resolution_y.")

            if "percentage" in params_source:
                try:
                    pct = int(params_source["percentage"])
                    if pct <= 0 or pct > 1000:
                        raise BlenderActionValidationError(f"resolution_percentage out of valid range (1-1000), got {pct}")
                    res["percentage"] = pct
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid integer for resolution percentage.")

            if "engine" in params_source:
                eng = str(params_source["engine"]).upper()
                allowed_engs = {"CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "EEVEE", "BLENDER_WORKBENCH", "WORKBENCH"}
                if eng not in allowed_engs:
                    raise BlenderActionValidationError(f"Unsupported render engine '{eng}'. Allowed: {allowed_engs}")
                res["engine"] = eng

            return res

        if action_type in cls.GEOMETRY_NODES_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type

            if "node_type" in params_source:
                ntype = str(params_source["node_type"])
                if ntype not in ALLOWED_NODE_TYPES:
                    raise BlenderActionValidationError(f"Unsupported geometry node_type '{ntype}'. Allowed: {ALLOWED_NODE_TYPES}")
                res["node_type"] = ntype

            if "socket_type" in params_source:
                stype = str(params_source["socket_type"])
                if stype not in ALLOWED_SOCKET_TYPES:
                    raise BlenderActionValidationError(f"Unsupported geometry socket_type '{stype}'. Allowed: {ALLOWED_SOCKET_TYPES}")
                res["socket_type"] = stype

            for n_field in ("group_name", "node_name", "from_node", "to_node", "socket_name", "new_name"):
                if n_field in params_source:
                    res[n_field] = cls.sanitize_name(str(params_source[n_field]))

            return res

        if action_type in cls.PHYSICS_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type

            if "collision_shape" in params_source:
                cshape = str(params_source["collision_shape"]).upper()
                if cshape not in ALLOWED_COLLISION_SHAPES:
                    raise BlenderActionValidationError(f"Unsupported collision_shape '{cshape}'. Allowed: {ALLOWED_COLLISION_SHAPES}")
                res["collision_shape"] = cshape

            if "field_type" in params_source:
                ftype = str(params_source["field_type"]).upper()
                if ftype not in ALLOWED_FORCE_FIELD_TYPES:
                    raise BlenderActionValidationError(f"Unsupported field_type '{ftype}'. Allowed: {ALLOWED_FORCE_FIELD_TYPES}")
                res["field_type"] = ftype

            if "fluid_type" in params_source:
                fltype = str(params_source["fluid_type"]).upper()
                if fltype not in ALLOWED_FLUID_TYPES:
                    raise BlenderActionValidationError(f"Unsupported fluid_type '{fltype}'. Allowed: {ALLOWED_FLUID_TYPES}")
                res["fluid_type"] = fltype

            if "object_name" in params_source or "name" in params_source or action.target_label:
                raw_name = params_source.get("object_name") or params_source.get("name") or action.target_label or "Object"
                res["object_name"] = cls.sanitize_name(raw_name)
                res["name"] = res["object_name"]

            return res

        if action_type in cls.ASSET_PIPELINE_ACTIONS:
            res = dict(params_source)
            res["action_type"] = action_type

            for path_key in ("filepath", "new_filepath", "output_directory", "directory"):
                if path_key in params_source and params_source[path_key]:
                    p_val = str(params_source[path_key])
                    if ".." in p_val or p_val.startswith("\\\\"):
                        raise BlenderActionValidationError(f"Path traversal or network path forbidden in '{path_key}': {p_val}")
                    res[path_key] = p_val.replace("\\", "/")

            if action_type == "export_gltf" and "export_format" in params_source:
                fmt = str(params_source["export_format"]).upper()
                if fmt not in ALLOWED_GLTF_FORMATS:
                    raise BlenderActionValidationError(f"Invalid glTF export_format '{fmt}'. Allowed: {ALLOWED_GLTF_FORMATS}")
                res["export_format"] = fmt

            return res

        if action_type in cls.MODIFIER_ACTIONS:
            # Flatten 'properties' dict if passed
            if isinstance(params_source.get("properties"), dict):
                for pk, pv in params_source["properties"].items():
                    params_source[pk] = pv

            raw_name = params_source.get("object_name") or params_source.get("name") or action.target_label or "Object"
            raw_mod_name = params_source.get("modifier_name") or params_source.get("mod_name") or params_source.get("new_name") or "Modifier"

            name = cls.sanitize_name(raw_name)
            mod_name = cls.sanitize_name(raw_mod_name)

            res = {
                "action_type": action_type,
                "name": name,
                "object_name": name,
                "modifier_name": mod_name,
                "mod_name": mod_name,
                "properties": {},
            }

            if action_type == "add_modifier":
                if "modifier_type" not in params_source and "type" not in params_source:
                    raise BlenderActionValidationError("Action 'add_modifier' requires 'modifier_type' parameter.")
                m_type = str(params_source.get("modifier_type") or params_source.get("type")).upper()
                if m_type not in BlenderModifierExecutor.ALLOWED_MODIFIERS:
                    raise BlenderActionValidationError(f"Unsupported modifier type '{m_type}'. Allowed: {BlenderModifierExecutor.ALLOWED_MODIFIERS}")
                res["modifier_type"] = m_type
                res["type"] = m_type

            if "modifier_type" in params_source or "type" in params_source:
                m_type = str(params_source.get("modifier_type") or params_source.get("type")).upper()
                if m_type not in BlenderModifierExecutor.ALLOWED_MODIFIERS:
                    raise BlenderActionValidationError(f"Unsupported modifier type '{m_type}'. Allowed: {BlenderModifierExecutor.ALLOWED_MODIFIERS}")
                res["modifier_type"] = m_type
                res["type"] = m_type

            if "new_name" in params_source:
                res["new_name"] = cls.sanitize_name(str(params_source["new_name"]))

            if "operand_object" in params_source or "object" in params_source:
                operand = cls.sanitize_name(str(params_source.get("operand_object") or params_source.get("object")))
                if operand == name:
                    raise BlenderActionValidationError("Boolean modifier operand object cannot target itself.")
                res["operand_object"] = operand
                res["object"] = operand
                res["properties"]["operand_object"] = operand

            if "direction" in params_source:
                direction = str(params_source["direction"]).lower()
                if direction not in ("move_up", "move_down", "move_to_index", "up", "down"):
                    raise BlenderActionValidationError(f"Invalid move direction '{direction}'.")
                res["direction"] = direction

            if "levels" in params_source:
                try:
                    lvl = int(params_source["levels"])
                    if lvl < 0 or lvl > 6:
                        raise BlenderActionValidationError(f"Subsurf levels {lvl} out of range (0..6).")
                    res["levels"] = lvl
                    res["properties"]["levels"] = lvl
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid integer for levels.")

            if "render_levels" in params_source:
                try:
                    rlvl = int(params_source["render_levels"])
                    if rlvl < 0 or rlvl > 6:
                        raise BlenderActionValidationError(f"Subsurf render_levels {rlvl} out of range (0..6).")
                    res["render_levels"] = rlvl
                    res["properties"]["render_levels"] = rlvl
                except (ValueError, TypeError):
                    raise BlenderActionValidationError("Invalid integer for render_levels.")

            if "object_offset" in params_source:
                res["object_offset"] = cls.sanitize_name(str(params_source["object_offset"]))

            for k in ("limit_method", "affect", "operation", "solver", "decimate_type", "mode", "subdivision_type"):
                if k in params_source:
                    res[k] = cls.sanitize_name(str(params_source[k]))
                    res["properties"][k] = res[k]

            for k in ("width", "offset", "thickness", "merge_threshold", "ratio", "angle_limit", "threshold", "distance"):
                if k in params_source:
                    try:
                        res[k] = float(params_source[k])
                        res["properties"][k] = res[k]
                    except (ValueError, TypeError):
                        res[k] = 0.1

            for k in ("segments", "cuts", "count", "iterations", "weight", "index", "to_index"):
                if k in params_source:
                    try:
                        res[k] = int(params_source[k])
                        res["properties"][k] = res[k]
                    except (ValueError, TypeError):
                        res[k] = 1

            for k in ("use_axis_x", "use_axis_y", "use_axis_z", "use_clip", "use_mirror_merge", "use_rim", "use_rim_only", "merge_vertices", "keep_sharp", "show_viewport", "show_render", "visible"):
                if k in params_source:
                    res[k] = bool(params_source[k])
                    res["properties"][k] = res[k]

            if "relative_offset" in params_source and isinstance(params_source["relative_offset"], (list, tuple)):
                res["relative_offset"] = cls.validate_vector3(params_source["relative_offset"])
                res["properties"]["relative_offset"] = res["relative_offset"]

            if "constant_offset" in params_source and isinstance(params_source["constant_offset"], (list, tuple)):
                res["constant_offset"] = cls.validate_vector3(params_source["constant_offset"])
                res["properties"]["constant_offset"] = res["constant_offset"]

            return res

        elif action_type in cls.MESH_ACTIONS:
            name = cls.sanitize_name(params_source.get("object_name") or params_source.get("name") or action.target_label or "Mesh")
            res = {"action_type": action_type, "name": name, "object_name": name}
            for k in ("primitive", "element_type", "type", "parent_collection", "collection", "target_object"):
                if k in params_source:
                    res[k] = cls.sanitize_name(str(params_source[k]))
            if "source_objects" in params_source:
                res["source_objects"] = [cls.sanitize_name(str(s)) for s in params_source["source_objects"]]
            for k in ("distance", "thickness", "amount", "scale_length", "offset", "width"):
                if k in params_source:
                    try:
                        res[k] = float(params_source[k])
                    except (ValueError, TypeError):
                        res[k] = 1.0
            for k in ("cuts", "segments", "v1", "v2"):
                if k in params_source:
                    try:
                        res[k] = int(params_source[k])
                    except (ValueError, TypeError):
                        res[k] = 1
            for k in ("indices", "vertex_indices", "face_indices"):
                if k in params_source and isinstance(params_source[k], (list, tuple)):
                    try:
                        res[k] = [int(i) for i in params_source[k]]
                    except (ValueError, TypeError):
                        res[k] = []
            if "location" in params_source:
                res["location"] = cls.validate_vector3(params_source["location"])
            if "inside" in params_source:
                res["inside"] = bool(params_source["inside"])
            return res

        elif action_type == "create_object":
            primitive = params_source.get("primitive", "cube").lower()
            if primitive not in cls.ALLOWED_PRIMITIVES:
                raise BlenderActionValidationError(
                    f"Invalid primitive '{primitive}'. Allowed primitives: {cls.ALLOWED_PRIMITIVES}"
                )
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Cube"))
            loc = cls.validate_vector3(params_source.get("location", [0.0, 0.0, 0.0]))
            return {"action_type": action_type, "primitive": primitive, "name": name, "location": loc}

        elif action_type in ("delete_object", "select_object"):
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Object"))
            return {"action_type": action_type, "name": name}

        elif action_type in ("move_object", "transform_object"):
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Object"))
            loc = cls.validate_vector3(params_source.get("location", [0.0, 0.0, 0.0]))
            rot = cls.validate_vector3(params_source.get("rotation", [0.0, 0.0, 0.0]))
            scale = cls.validate_vector3(params_source.get("scale", [1.0, 1.0, 1.0]))
            return {"action_type": action_type, "name": name, "location": loc, "rotation": rot, "scale": scale}

        elif action_type == "rename_object":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Object"))
            new_name = cls.sanitize_name(str(action.value or params_source.get("new_name", "NewName")))
            return {"action_type": action_type, "name": name, "new_name": new_name}

        elif action_type in ("create_material", "set_material_properties"):
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Material"))
            color = cls.validate_vector4(params_source.get("base_color", [0.8, 0.8, 0.8, 1.0]))
            metallic = cls.clamp_float(params_source.get("metallic", 0.0))
            roughness = cls.clamp_float(params_source.get("roughness", 0.5))
            return {
                "action_type": action_type,
                "name": name,
                "base_color": color,
                "metallic": metallic,
                "roughness": roughness,
            }

        elif action_type == "create_camera":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Camera"))
            loc = cls.validate_vector3(params_source.get("location", [0.0, -10.0, 5.0]))
            return {"action_type": action_type, "name": name, "location": loc}

        elif action_type == "create_light":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Light"))
            light_type = str(params_source.get("light_type", "POINT")).upper()
            if light_type not in cls.ALLOWED_LIGHT_TYPES:
                light_type = "POINT"
            loc = cls.validate_vector3(params_source.get("location", [4.0, 1.0, 6.0]))
            return {"action_type": action_type, "name": name, "light_type": light_type, "location": loc}

        elif action_type in ("save_file", "blender_save_file"):
            filepath = action.target_label or params_source.get("filepath", "scene.blend")
            if ".." in filepath or ";" in filepath or "|" in filepath:
                raise BlenderActionValidationError("Invalid characters in save filepath.")
            filepath = filepath.replace("\\", "/")
            return {"action_type": action_type, "filepath": filepath}

        # Scene actions
        elif action_type == "create_scene":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Scene"))
            return {"action_type": action_type, "name": name}

        elif action_type == "delete_scene":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Scene"))
            return {"action_type": action_type, "name": name}

        elif action_type == "rename_scene":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Scene"))
            new_name = cls.sanitize_name(str(action.value or params_source.get("new_name", "NewScene")))
            return {"action_type": action_type, "name": name, "new_name": new_name}

        elif action_type == "set_scene_units":
            system = str(params_source.get("system", "METRIC")).upper()
            if system not in cls.ALLOWED_UNIT_SYSTEMS:
                system = "METRIC"
            scale = float(params_source.get("scale_length", 1.0))
            return {"action_type": action_type, "system": system, "scale_length": scale}

        elif action_type == "create_collection":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Collection"))
            parent = cls.sanitize_name(params_source.get("parent_collection", "")) if params_source.get("parent_collection") else None
            return {"action_type": action_type, "name": name, "parent_collection": parent}

        elif action_type == "delete_collection":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Collection"))
            return {"action_type": action_type, "name": name}

        elif action_type == "rename_collection":
            name = cls.sanitize_name(action.target_label or params_source.get("name", "Collection"))
            new_name = cls.sanitize_name(str(action.value or params_source.get("new_name", "NewCollection")))
            return {"action_type": action_type, "name": name, "new_name": new_name}

        elif action_type in ("link_object_to_collection", "unlink_object_from_collection"):
            obj_name = cls.sanitize_name(params_source.get("object_name") or params_source.get("object") or action.target_label or "")
            col_name = cls.sanitize_name(params_source.get("collection_name") or params_source.get("collection") or "")
            if not obj_name or not col_name:
                raise BlenderActionValidationError(f"Action '{action_type}' requires object_name and collection_name.")
            return {"action_type": action_type, "object_name": obj_name, "collection_name": col_name}

        # Object Hierarchy actions
        elif action_type == "duplicate_object":
            source = cls.sanitize_name(params_source.get("source_object") or params_source.get("name") or action.target_label or "Cube")
            new_name = cls.sanitize_name(params_source.get("new_name", "")) if params_source.get("new_name") else None
            return {"action_type": action_type, "source_object": source, "new_name": new_name}

        elif action_type in ("hide_object", "show_object"):
            name = cls.sanitize_name(params_source.get("object_name") or params_source.get("name") or action.target_label or "Object")
            return {
                "action_type": action_type,
                "name": name,
                "hide_viewport": bool(params_source.get("hide_viewport", True)),
                "hide_render": bool(params_source.get("hide_render", True)),
                "show_viewport": bool(params_source.get("show_viewport", True)),
                "show_render": bool(params_source.get("show_render", True)),
            }

        elif action_type == "apply_transform":
            name = cls.sanitize_name(params_source.get("object_name") or params_source.get("name") or action.target_label or "Object")
            return {
                "action_type": action_type,
                "name": name,
                "location": bool(params_source.get("location", True)),
                "rotation": bool(params_source.get("rotation", True)),
                "scale": bool(params_source.get("scale", True)),
            }

        elif action_type == "parent_object":
            raw_child = params_source.get("child") or action.target_label
            raw_parent = params_source.get("parent")
            if not raw_child or not raw_parent:
                raise BlenderActionValidationError("Action 'parent_object' requires 'child' and 'parent' parameters.")
            child = cls.sanitize_name(raw_child)
            parent = cls.sanitize_name(raw_parent)
            return {"action_type": action_type, "child": child, "parent": parent, "keep_transform": bool(params_source.get("keep_transform", True))}

        elif action_type == "unparent_object":
            raw_child = params_source.get("child") or action.target_label
            if not raw_child:
                raise BlenderActionValidationError("Action 'unparent_object' requires 'child' parameter.")
            child = cls.sanitize_name(raw_child)
            return {"action_type": action_type, "child": child, "keep_transform": bool(params_source.get("keep_transform", True))}

        elif action_type == "add_constraint":
            name = cls.sanitize_name(params_source.get("object_name") or params_source.get("name") or action.target_label or "Object")
            c_type = str(params_source.get("constraint_type", "COPY_LOCATION")).upper()
            if c_type not in BlenderObjectExecutor.ALLOWED_CONSTRAINTS:
                raise BlenderActionValidationError(f"Constraint type '{c_type}' not allowed. Allowed: {BlenderObjectExecutor.ALLOWED_CONSTRAINTS}")
            target = cls.sanitize_name(params_source.get("target_object", "")) if params_source.get("target_object") else None
            c_name = cls.sanitize_name(params_source.get("constraint_name", "")) if params_source.get("constraint_name") else None
            return {"action_type": action_type, "name": name, "constraint_type": c_type, "target_object": target, "constraint_name": c_name}

        elif action_type == "remove_constraint":
            name = cls.sanitize_name(params_source.get("object_name") or params_source.get("name") or action.target_label or "Object")
            c_name = cls.sanitize_name(params_source.get("constraint_name") or params_source.get("constraint") or "")
            if not c_name:
                raise BlenderActionValidationError("Action 'remove_constraint' requires 'constraint_name' parameter.")
            return {"action_type": action_type, "name": name, "constraint_name": c_name}

        else:
            raise BlenderActionValidationError(f"Action '{action.action_type}' is not supported by Blender validator.")

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitizes object/material/scene/collection names to prevent code injection."""
        s_name = str(name).strip()
        forbidden_sub = [";", "'", '"', "import ", "exec", "eval", "os.system", "script"]
        if any(f in s_name for f in forbidden_sub):
            raise BlenderActionValidationError(f"Name '{s_name}' contains forbidden string or character.")
        sanitized = re.sub(r"[^\w\.-]", "_", s_name)
        return sanitized[:64] or "Object"

    @staticmethod
    def validate_vector3(val: Any) -> Tuple[float, float, float]:
        """Validates 3D vector coordinates."""
        if isinstance(val, (list, tuple)) and len(val) >= 3:
            try:
                return (float(val[0]), float(val[1]), float(val[2]))
            except (ValueError, TypeError):
                pass
        return (0.0, 0.0, 0.0)

    @staticmethod
    def validate_vector4(val: Any) -> Tuple[float, float, float, float]:
        """Validates RGBA color vector."""
        if isinstance(val, (list, tuple)) and len(val) >= 4:
            try:
                return (
                    max(0.0, min(1.0, float(val[0]))),
                    max(0.0, min(1.0, float(val[1]))),
                    max(0.0, min(1.0, float(val[2]))),
                    max(0.0, min(1.0, float(val[3]))),
                )
            except (ValueError, TypeError):
                pass
        return (0.8, 0.8, 0.8, 1.0)

    @staticmethod
    def clamp_float(val: Any) -> float:
        """Clamps float between 0.0 and 1.0."""
        try:
            return max(0.0, min(1.0, float(val)))
        except (ValueError, TypeError):
            return 0.5


class BlenderBpyExecutor:
    """Builds and executes validated template-based BPY scripts cleanly.

    Ensures zero arbitrary Python string execution.
    """

    @classmethod
    def build_bpy_script(cls, params: Dict[str, Any]) -> str:
        """Constructs BPY script from validated parameters using domain executors."""
        action_type = params["action_type"]

        if action_type in BlenderActionValidator.SCENE_ACTIONS:
            return BlenderSceneExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.OBJECT_HIERARCHY_ACTIONS:
            return BlenderObjectExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.MESH_ACTIONS:
            return BlenderMeshExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.MODIFIER_ACTIONS:
            return BlenderModifierExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.MATERIAL_ACTIONS:
            return BlenderMaterialExecutor.build_bpy_script(action_type, params)

        if action_type in BlenderActionValidator.CAMERA_LIGHTING_ACTIONS:
            return BlenderCameraLightingExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.ANIMATION_ACTIONS:
            return BlenderAnimationExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.RENDER_ACTIONS:
            return BlenderRenderExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.GEOMETRY_NODES_ACTIONS:
            return BlenderGeometryNodesExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.PHYSICS_ACTIONS:
            return BlenderPhysicsExecutor.build_script(action_type, params)

        if action_type in BlenderActionValidator.ASSET_PIPELINE_ACTIONS:
            return BlenderAssetPipelineExecutor.build_script(action_type, params)


        if action_type == "create_object":
            prim = params["primitive"]
            x, y, z = params["location"]
            name = params["name"]
            if prim == "cube":
                bpy_op = f"bpy.ops.mesh.primitive_cube_add(location=({x}, {y}, {z}))"
            elif prim in ("uv_sphere", "sphere"):
                bpy_op = f"bpy.ops.mesh.primitive_uv_sphere_add(location=({x}, {y}, {z}))"
            elif prim == "icosphere":
                bpy_op = f"bpy.ops.mesh.primitive_icosphere_add(location=({x}, {y}, {z}))"
            elif prim == "cylinder":
                bpy_op = f"bpy.ops.mesh.primitive_cylinder_add(location=({x}, {y}, {z}))"
            else:
                bpy_op = f"bpy.ops.mesh.primitive_plane_add(location=({x}, {y}, {z}))"

            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"{bpy_op}\n"
                "obj = bpy.context.active_object\n"
                "if obj:\n"
                f"    obj.name = '{name}'\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "delete_object":
            name = params["name"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.data.objects.remove(obj, do_unlink=True)\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type in ("move_object", "transform_object"):
            name = params["name"]
            x, y, z = params["location"]
            rx, ry, rz = params.get("rotation", (0.0, 0.0, 0.0))
            sx, sy, sz = params.get("scale", (1.0, 1.0, 1.0))
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    obj.location = ({x}, {y}, {z})\n"
                f"    obj.rotation_euler = ({rx}, {ry}, {rz})\n"
                f"    obj.scale = ({sx}, {sy}, {sz})\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "rename_object":
            name = params["name"]
            new_name = params["new_name"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                f"    obj.name = '{new_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{new_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type in ("create_material", "set_material_properties"):
            name = params["name"]
            r, g, b, a = params["base_color"]
            met = params["metallic"]
            rough = params["roughness"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = bpy.data.materials.get('{name}') or bpy.data.materials.new(name='{name}')\n"
                "mat.use_nodes = True\n"
                "bsdf = mat.node_tree.nodes.get('Principled BSDF')\n"
                "if bsdf:\n"
                f"    bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, {a})\n"
                f"    bsdf.inputs['Metallic'].default_value = {met}\n"
                f"    bsdf.inputs['Roughness'].default_value = {rough}\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "select_object":
            name = params["name"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        elif action_type == "create_camera":
            name = params["name"]
            x, y, z = params["location"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"bpy.ops.object.camera_add(location=({x}, {y}, {z}))\n"
                "cam = bpy.context.active_object\n"
                "if cam:\n"
                f"    cam.name = '{name}'\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "create_light":
            name = params["name"]
            ltype = params["light_type"]
            x, y, z = params["location"]
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"bpy.ops.object.light_add(type='{ltype}', location=({x}, {y}, {z}))\n"
                "light = bpy.context.active_object\n"
                "if light:\n"
                f"    light.name = '{name}'\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type in ("save_file", "blender_save_file"):
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"bpy.ops.wm.save_as_mainfile(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{filepath}')\n"
            )

        raise ValueError(f"No BPY template for action '{action_type}'")

    async def execute_bpy(self, params: Dict[str, Any], is_blender_running: bool = False, blend_filepath: Optional[str] = None, timeout: float = 30.0) -> AutomationResult:
        """Executes constructed BPY script via local Blender environment or returns failure if unavailable."""
        action_type = params.get("action_type", "unknown")
        script_code = self.build_bpy_script(params)

        if blend_filepath and os.path.exists(blend_filepath):
            clean_path = blend_filepath.replace("\\", "/")
            script_code += f"\nif bpy.data.filepath:\n    bpy.ops.wm.save_mainfile()\nelse:\n    bpy.ops.wm.save_as_mainfile(filepath='{clean_path}')\n"

        blender_executable = self.find_blender_executable()
        if not blender_executable and not is_blender_running:
            logger.warning("Blender executable not found on host system")
            return AutomationResult(
                action_id=params.get("action_id", "act_blender"),
                success=False,
                output=None,
                error_message="Blender application or executable is not available on system.",
                duration_sec=0.0,
            )

        start_time = time.time()
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(script_code)
                script_path = f.name

            cmd = [blender_executable or "blender"]
            if blend_filepath and os.path.exists(blend_filepath):
                cmd.append(blend_filepath)
            cmd.extend(["--background", "--python", script_path])

            timeout_val = float(params.get("timeout", timeout))
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_val,
            )
            os.remove(script_path)

            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            combined_output = stdout + "\n" + stderr

            success_marker = f"NOVA_ACTION_SUCCESS::{action_type}"
            has_success = success_marker in stdout
            has_error_marker = "NOVA_ACTION_ERROR::" in stdout or "ERROR_" in stdout

            traceback_terms = [
                "Traceback (most recent call last):",
                "NameError:",
                "SyntaxError:",
                "RuntimeError:",
                "TypeError:",
                "ValueError:",
                "ReferenceError:",
                "AttributeError:",
                "IndentationError:",
                "ZeroDivisionError:",
                "KeyError:",
                "IndexError:",
                "Exception:",
            ]
            has_exception = any(term in combined_output for term in traceback_terms)

            if proc.returncode == 0 and has_success and not has_error_marker and not has_exception:
                return AutomationResult(
                    action_id=params.get("action_id", "act_blender"),
                    success=True,
                    output={"stdout": stdout.strip(), "params": params},
                    duration_sec=time.time() - start_time,
                )
            else:
                clean_stderr = "\n".join([line for line in stderr.splitlines() if "DeprecationWarning" not in line and "Warning" not in line]).strip()
                if has_error_marker:
                    err_msg = stdout.strip()
                else:
                    err_msg = (stdout.strip() + "\n" + clean_stderr).strip() if stdout.strip() else (clean_stderr or stderr.strip())
                if not has_success and not has_exception and not has_error_marker:
                    err_msg = f"Missing success marker '{success_marker}'. Output: {err_msg}"
                return AutomationResult(
                    action_id=params.get("action_id", "act_blender"),
                    success=False,
                    error_message=f"BPY execution failed: {err_msg}",
                    duration_sec=time.time() - start_time,
                )
        except Exception as e:
            return AutomationResult(
                action_id=params.get("action_id", "act_blender"),
                success=False,
                error_message=f"Blender execution error: {str(e)}",
                duration_sec=time.time() - start_time,
            )

    @staticmethod
    def find_blender_executable() -> Optional[str]:
        """Finds blender.exe on system path or standard Windows install locations."""
        import shutil
        import glob

        path_cmd = shutil.which("blender")
        if path_cmd:
            return path_cmd

        found = glob.glob("C:\\Program Files\\Blender Foundation\\*\\blender.exe")
        if found:
            return found[0]

        for loc in [
            "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
        ]:
            if os.path.exists(loc):
                return loc
        return None
