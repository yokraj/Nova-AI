"""Blender BPY Action Validator and Controlled Execution Engine.

Enforces strict parameter validation and template-based BPY script generation.
NEVER executes raw or arbitrary AI-generated Python strings directly.
"""

from typing import Any, Dict, List, Optional, Tuple
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

logger = structlog.get_logger("blender_adapter")


class BlenderActionValidationError(Exception):
    """Raised when Blender action parameters fail validation."""

    pass


class BlenderActionValidator:
    """Validates Blender operation parameters against strict schemas before execution."""

    ALLOWED_PRIMITIVES = {"cube", "uv_sphere", "icosphere", "cylinder", "plane"}
    ALLOWED_LIGHT_TYPES = {"POINT", "SUN", "SPOT", "AREA"}

    @classmethod
    def validate_action(cls, action: AutomationAction) -> Dict[str, Any]:
        """Validates action parameter schema and returns sanitized parameter dictionary."""
        action_type = action.action_type.lower()

        if action_type == "create_object":
            primitive = action.selector.get("primitive", "cube").lower()
            if primitive not in cls.ALLOWED_PRIMITIVES:
                raise BlenderActionValidationError(
                    f"Invalid primitive '{primitive}'. Allowed primitives: {cls.ALLOWED_PRIMITIVES}"
                )
            name = cls.sanitize_name(action.target_label or "Cube")
            loc = cls.validate_vector3(action.selector.get("location", [0.0, 0.0, 0.0]))
            return {"action_type": action_type, "primitive": primitive, "name": name, "location": loc}

        elif action_type in ("delete_object", "select_object"):
            name = cls.sanitize_name(action.target_label or "Object")
            return {"action_type": action_type, "name": name}

        elif action_type in ("move_object", "transform_object"):
            name = cls.sanitize_name(action.target_label or "Object")
            loc = cls.validate_vector3(action.selector.get("location", [0.0, 0.0, 0.0]))
            rot = cls.validate_vector3(action.selector.get("rotation", [0.0, 0.0, 0.0]))
            scale = cls.validate_vector3(action.selector.get("scale", [1.0, 1.0, 1.0]))
            return {"action_type": action_type, "name": name, "location": loc, "rotation": rot, "scale": scale}

        elif action_type == "rename_object":
            name = cls.sanitize_name(action.target_label or "Object")
            new_name = cls.sanitize_name(str(action.value or "NewName"))
            return {"action_type": action_type, "name": name, "new_name": new_name}

        elif action_type in ("create_material", "set_material_properties"):
            name = cls.sanitize_name(action.target_label or "Material")
            color = cls.validate_vector4(action.selector.get("base_color", [0.8, 0.8, 0.8, 1.0]))
            metallic = cls.clamp_float(action.selector.get("metallic", 0.0))
            roughness = cls.clamp_float(action.selector.get("roughness", 0.5))
            return {
                "action_type": action_type,
                "name": name,
                "base_color": color,
                "metallic": metallic,
                "roughness": roughness,
            }

        elif action_type == "create_camera":
            name = cls.sanitize_name(action.target_label or "Camera")
            loc = cls.validate_vector3(action.selector.get("location", [0.0, -10.0, 5.0]))
            return {"action_type": action_type, "name": name, "location": loc}

        elif action_type == "create_light":
            name = cls.sanitize_name(action.target_label or "Light")
            light_type = str(action.selector.get("light_type", "POINT")).upper()
            if light_type not in cls.ALLOWED_LIGHT_TYPES:
                light_type = "POINT"
            loc = cls.validate_vector3(action.selector.get("location", [4.0, 1.0, 6.0]))
            return {"action_type": action_type, "name": name, "light_type": light_type, "location": loc}

        elif action_type in ("save_file", "blender_save_file"):
            filepath = action.target_label or "scene.blend"
            if ".." in filepath or ";" in filepath or "|" in filepath:
                raise BlenderActionValidationError("Invalid characters in save filepath.")
            return {"action_type": action_type, "filepath": filepath}

        else:
            raise BlenderActionValidationError(f"Action '{action.action_type}' is not supported by Blender validator.")

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitizes object/material names to prevent code injection."""
        sanitized = re.sub(r"[^\w\.-]", "_", name.strip())
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
        """Constructs BPY script from validated parameters using fixed templates."""
        action_type = params["action_type"]

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

            return f"import bpy\n{bpy_op}\nobj = bpy.context.active_object\nif obj:\n    obj.name = '{name}'\nprint(f'CREATED_OBJECT::{name}')\n"

        elif action_type == "delete_object":
            name = params["name"]
            return f"import bpy\nobj = bpy.data.objects.get('{name}')\nif obj:\n    bpy.data.objects.remove(obj, do_unlink=True)\nprint(f'DELETED_OBJECT::{name}')\n"

        elif action_type in ("move_object", "transform_object"):
            name = params["name"]
            x, y, z = params["location"]
            rx, ry, rz = params.get("rotation", (0.0, 0.0, 0.0))
            sx, sy, sz = params.get("scale", (1.0, 1.0, 1.0))
            return f"import bpy\nobj = bpy.data.objects.get('{name}')\nif obj:\n    obj.location = ({x}, {y}, {z})\n    obj.rotation_euler = ({rx}, {ry}, {rz})\n    obj.scale = ({sx}, {sy}, {sz})\nprint(f'MOVED_OBJECT::{name}')\n"

        elif action_type == "rename_object":
            name = params["name"]
            new_name = params["new_name"]
            return f"import bpy\nobj = bpy.data.objects.get('{name}')\nif obj:\n    obj.name = '{new_name}'\nprint(f'RENAMED_OBJECT::{new_name}')\n"

        elif action_type in ("create_material", "set_material_properties"):
            name = params["name"]
            r, g, b, a = params["base_color"]
            met = params["metallic"]
            rough = params["roughness"]
            return f"import bpy\nmat = bpy.data.materials.get('{name}') or bpy.data.materials.new(name='{name}')\nmat.use_nodes = True\nbsdf = mat.node_tree.nodes.get('Principled BSDF')\nif bsdf:\n    bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, {a})\n    bsdf.inputs['Metallic'].default_value = {met}\n    bsdf.inputs['Roughness'].default_value = {rough}\nprint(f'MATERIAL_SET::{name}')\n"

        elif action_type == "select_object":
            name = params["name"]
            return f"import bpy\nobj = bpy.data.objects.get('{name}')\nif obj:\n    bpy.ops.object.select_all(action='DESELECT')\n    obj.select_set(True)\n    bpy.context.view_layer.objects.active = obj\nprint(f'SELECTED_OBJECT::{name}')\n"

        elif action_type == "create_camera":
            name = params["name"]
            x, y, z = params["location"]
            return f"import bpy\nbpy.ops.object.camera_add(location=({x}, {y}, {z}))\ncam = bpy.context.active_object\nif cam:\n    cam.name = '{name}'\nprint(f'CREATED_CAMERA::{name}')\n"

        elif action_type == "create_light":
            name = params["name"]
            ltype = params["light_type"]
            x, y, z = params["location"]
            return f"import bpy\nbpy.ops.object.light_add(type='{ltype}', location=({x}, {y}, {z}))\nlight = bpy.context.active_object\nif light:\n    light.name = '{name}'\nprint(f'CREATED_LIGHT::{name}')\n"

        elif action_type in ("save_file", "blender_save_file"):
            filepath = params["filepath"]
            return f"import bpy\nbpy.ops.wm.save_as_mainfile(filepath='{filepath}')\nprint(f'SAVED_FILE::{filepath}')\n"

        raise ValueError(f"No BPY template for action '{action_type}'")

    async def execute_bpy(self, params: Dict[str, Any], is_blender_running: bool = False) -> AutomationResult:
        """Executes constructed BPY script via local Blender environment or returns failure if unavailable."""
        script_code = self.build_bpy_script(params)

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

            proc = subprocess.run(
                [blender_executable or "blender", "--background", "--python", script_path],
                capture_output=True,
                text=True,
                timeout=15,
            )
            os.remove(script_path)

            if proc.returncode == 0:
                return AutomationResult(
                    action_id=params.get("action_id", "act_blender"),
                    success=True,
                    output={"stdout": proc.stdout.strip(), "params": params},
                    duration_sec=time.time() - start_time,
                )
            else:
                return AutomationResult(
                    action_id=params.get("action_id", "act_blender"),
                    success=False,
                    error_message=f"BPY script execution failed: {proc.stderr.strip() or proc.stdout.strip()}",
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
