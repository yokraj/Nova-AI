"""Blender Camera & Lighting Subsystem Executor.

Implements structured BPY script generation for 48 Camera and Lighting actions:
- Camera Lifecycle & Optics (creation, deletion, active camera, lens, sensor, clip, shift, DOF, targeting)
- Light Lifecycle & Transforms (Point, Sun, Spot, Area, location, rotation, aiming)
- Light Properties & Color Temperature (energy, RGB color, Kelvin blackbody conversion, spot angle/blend, shadow settings)
- Scene Lighting Inspection & Validation
"""

from typing import Any, Dict, Set
import math


class BlenderCameraLightingExecutor:
    """Generates validated BPY script templates for Blender camera and lighting operations."""

    ALLOWED_CAMERA_TYPES: Set[str] = {"PERSP", "ORTHO", "PANO"}
    ALLOWED_LIGHT_TYPES: Set[str] = {"POINT", "SUN", "SPOT", "AREA"}

    @staticmethod
    def kelvin_to_rgb(kelvin: float) -> list[float]:
        """Convert Kelvin temperature (1000K - 12000K) to normalized RGB [0.0, 1.0]."""
        temp = max(1000.0, min(12000.0, float(kelvin))) / 100.0
        # Red
        if temp <= 66:
            r = 255.0
        else:
            r = 329.698727446 * ((temp - 60.0) ** -0.1332047592)
            r = max(0.0, min(255.0, r))
        # Green
        if temp <= 66:
            g = 99.4708025861 * math.log(temp) - 161.1195681661
        else:
            g = 288.1221695283 * ((temp - 60.0) ** -0.0755148492)
        g = max(0.0, min(255.0, g))
        # Blue
        if temp >= 66:
            b = 255.0
        elif temp <= 19:
            b = 0.0
        else:
            b = 138.5177312231 * math.log(temp - 10.0) - 305.0447927307
            b = max(0.0, min(255.0, b))
        return [round(r / 255.0, 4), round(g / 255.0, 4), round(b / 255.0, 4)]

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Build script based on action_type."""
        method_name = f"_build_{action_type}"
        handler = getattr(cls, method_name, None)
        if not handler:
            raise ValueError(f"Unsupported camera/lighting action_type: {action_type}")
        return handler(params)

    # -------------------------------------------------------------------------
    # A. CAMERA LIFECYCLE
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name") or "Camera"
        lens = float(params.get("lens", 50.0))
        clip_start = float(params.get("clip_start", 0.1))
        clip_end = float(params.get("clip_end", 1000.0))
        cam_type = params.get("camera_type", "PERSP")
        loc = params.get("location", [0.0, -10.0, 5.0])
        rot = params.get("rotation", [1.1, 0.0, 0.0])

        return f"""import bpy
print('NOVA_ACTION_START::create_camera')
try:
    cam_data = bpy.data.cameras.new(name='{name}')
    cam_data.lens = {lens}
    cam_data.clip_start = {clip_start}
    cam_data.clip_end = {clip_end}
    cam_data.type = '{cam_type}'
    cam_obj = bpy.data.objects.new(name='{name}', object_data=cam_data)
    cam_obj.name = '{name}'
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    cam_obj.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})
    
    assert cam_obj.name in bpy.data.objects
    assert cam_obj.type == 'CAMERA'
    print(f'NOVA_ACTION_SUCCESS::create_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::create_camera::{{str(e)}}')
"""

    @classmethod
    def _build_delete_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name") or "Camera"
        return f"""import bpy
print('NOVA_ACTION_START::delete_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera object '{name}' not found")
    cam_data = cam_obj.data
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    if cam_data.users == 0:
        bpy.data.cameras.remove(cam_data)
    assert '{name}' not in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::delete_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::delete_camera::{{str(e)}}')
"""

    @classmethod
    def _build_rename_camera(cls, params: Dict[str, Any]) -> str:
        old_name = params.get("camera_name") or params.get("name")
        new_name = params.get("new_name", "RenamedCamera")
        return f"""import bpy
print('NOVA_ACTION_START::rename_camera')
try:
    cam_obj = bpy.data.objects.get('{old_name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{old_name}' not found")
    cam_obj.name = '{new_name}'
    cam_obj.data.name = '{new_name}'
    assert '{new_name}' in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::rename_camera::{new_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::rename_camera::{{str(e)}}')
"""

    @classmethod
    def _build_duplicate_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        new_name = params.get("new_name") or f"{name}_copy"
        return f"""import bpy
print('NOVA_ACTION_START::duplicate_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    new_data = cam_obj.data.copy()
    new_obj = cam_obj.copy()
    new_obj.data = new_data
    new_obj.name = '{new_name}'
    bpy.context.scene.collection.objects.link(new_obj)
    assert new_obj.name in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::duplicate_camera::{new_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::duplicate_camera::{{str(e)}}')
"""

    @classmethod
    def _build_get_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::get_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam = cam_obj.data
    info = f"name={{cam_obj.name}}:type={{cam.type}}:lens={{cam.lens}}:loc={{list(cam_obj.location)}}"
    print(f'NOVA_ACTION_SUCCESS::get_camera::{{info}}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_camera::{{str(e)}}')
"""

    @classmethod
    def _build_get_cameras(cls, params: Dict[str, Any]) -> str:
        return """import bpy
print('NOVA_ACTION_START::get_cameras')
try:
    cams = [o.name for o in bpy.data.objects if o.type == 'CAMERA']
    print(f'NOVA_ACTION_SUCCESS::get_cameras::{",".join(cams)}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_cameras::{str(e)}')
"""

    @classmethod
    def _build_set_active_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::set_active_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    bpy.context.scene.camera = cam_obj
    assert bpy.context.scene.camera == cam_obj
    print(f'NOVA_ACTION_SUCCESS::set_active_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_active_camera::{{str(e)}}')
"""

    # -------------------------------------------------------------------------
    # B. CAMERA TRANSFORM & TARGETING
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_camera_location(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        loc = params.get("location", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_location')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    print(f'NOVA_ACTION_SUCCESS::set_camera_location::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_location::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_rotation(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        rot = params.get("rotation", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_rotation')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})
    print(f'NOVA_ACTION_SUCCESS::set_camera_rotation::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_rotation::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_transform(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        loc = params.get("location", [0.0, 0.0, 0.0])
        rot = params.get("rotation", [0.0, 0.0, 0.0])
        scale = params.get("scale", [1.0, 1.0, 1.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_transform')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    cam_obj.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})
    cam_obj.scale = ({scale[0]}, {scale[1]}, {scale[2]})
    print(f'NOVA_ACTION_SUCCESS::set_camera_transform::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_transform::{{str(e)}}')
"""

    @classmethod
    def _build_move_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        delta = params.get("delta", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::move_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.location.x += {delta[0]}
    cam_obj.location.y += {delta[1]}
    cam_obj.location.z += {delta[2]}
    print(f'NOVA_ACTION_SUCCESS::move_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::move_camera::{{str(e)}}')
"""

    @classmethod
    def _build_rotate_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        delta = params.get("delta", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::rotate_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.rotation_euler.x += {delta[0]}
    cam_obj.rotation_euler.y += {delta[1]}
    cam_obj.rotation_euler.z += {delta[2]}
    print(f'NOVA_ACTION_SUCCESS::rotate_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::rotate_camera::{{str(e)}}')
"""

    @classmethod
    def _build_point_camera_at(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        target_obj_name = params.get("target_object")
        target_loc = params.get("target_location")

        if target_obj_name:
            target_expr = f"bpy.data.objects.get('{target_obj_name}').location"
        elif target_loc:
            target_expr = f"Vector(({target_loc[0]}, {target_loc[1]}, {target_loc[2]}))"
        else:
            target_expr = "Vector((0.0, 0.0, 0.0))"

        return f"""import bpy
from mathutils import Vector
print('NOVA_ACTION_START::point_camera_at')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    target = {target_expr}
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    print(f'NOVA_ACTION_SUCCESS::point_camera_at::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::point_camera_at::{{str(e)}}')
"""

    @classmethod
    def _build_track_camera_to_object(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        target_name = params.get("target_object", "Cube")
        track_axis = params.get("track_axis", "TRACK_NEGATIVE_Z")
        up_axis = params.get("up_axis", "UP_Y")
        return f"""import bpy
print('NOVA_ACTION_START::track_camera_to_object')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    target_obj = bpy.data.objects.get('{target_name}')
    if not target_obj:
        raise ValueError("Target object '{target_name}' not found")
    
    constraint = None
    for c in cam_obj.constraints:
        if c.type == 'TRACK_TO':
            constraint = c
            break
    if not constraint:
        constraint = cam_obj.constraints.new(type='TRACK_TO')
    constraint.target = target_obj
    constraint.track_axis = '{track_axis}'
    constraint.up_axis = '{up_axis}'
    
    assert constraint.target == target_obj
    print(f'NOVA_ACTION_SUCCESS::track_camera_to_object::{name}->{target_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::track_camera_to_object::{{str(e)}}')
"""

    # -------------------------------------------------------------------------
    # C. CAMERA OPTICS & DOF
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_camera_lens(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        lens = float(params.get("lens", 50.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_lens')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.lens = {lens}
    print(f'NOVA_ACTION_SUCCESS::set_camera_lens::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_lens::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_sensor(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        sw = params.get("sensor_width")
        sh = params.get("sensor_height")
        ops = []
        if sw is not None:
            ops.append(f"cam_obj.data.sensor_width = float({sw})")
        if sh is not None:
            ops.append(f"cam_obj.data.sensor_height = float({sh})")
        ops_str = "\n    ".join(ops) if ops else "pass"

        return f"""import bpy
print('NOVA_ACTION_START::set_camera_sensor')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    {ops_str}
    print(f'NOVA_ACTION_SUCCESS::set_camera_sensor::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_sensor::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_clip_start(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        clip_start = float(params.get("clip_start", 0.1))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_clip_start')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.clip_start = {clip_start}
    print(f'NOVA_ACTION_SUCCESS::set_camera_clip_start::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_clip_start::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_clip_end(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        clip_end = float(params.get("clip_end", 1000.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_clip_end')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.clip_end = {clip_end}
    print(f'NOVA_ACTION_SUCCESS::set_camera_clip_end::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_clip_end::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_shift(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        sx = float(params.get("shift_x", 0.0))
        sy = float(params.get("shift_y", 0.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_shift')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.shift_x = {sx}
    cam_obj.data.shift_y = {sy}
    print(f'NOVA_ACTION_SUCCESS::set_camera_shift::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_shift::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_type(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        cam_type = params.get("camera_type", "PERSP")
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_type')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.type = '{cam_type}'
    print(f'NOVA_ACTION_SUCCESS::set_camera_type::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_type::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_dof(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        use_dof = bool(params.get("use_dof", True))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_dof')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.dof.use_dof = {use_dof}
    print(f'NOVA_ACTION_SUCCESS::set_camera_dof::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_dof::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_dof_distance(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        dist = float(params.get("distance", 5.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_dof_distance')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam_obj.data.dof.focus_distance = {dist}
    print(f'NOVA_ACTION_SUCCESS::set_camera_dof_distance::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_dof_distance::{{str(e)}}')
"""

    @classmethod
    def _build_set_camera_dof_object(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        target_name = params.get("target_object")
        return f"""import bpy
print('NOVA_ACTION_START::set_camera_dof_object')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    target_obj = bpy.data.objects.get('{target_name}') if '{target_name}' else None
    cam_obj.data.dof.focus_object = target_obj
    print(f'NOVA_ACTION_SUCCESS::set_camera_dof_object::{name}->{target_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_camera_dof_object::{{str(e)}}')
"""

    @classmethod
    def _build_get_camera_state(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::get_camera_state')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' not found")
    cam = cam_obj.data
    dof = cam.dof
    f_obj = dof.focus_object.name if dof.focus_object else None
    info = f"name={{cam_obj.name}}:type={{cam.type}}:lens={{cam.lens}}:clip_start={{cam.clip_start}}:clip_end={{cam.clip_end}}:dof={{dof.use_dof}}:focus_dist={{dof.focus_distance}}:focus_obj={{f_obj}}"
    print(f'NOVA_ACTION_SUCCESS::get_camera_state::{{info}}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_camera_state::{{str(e)}}')
"""

    # -------------------------------------------------------------------------
    # D. LIGHT LIFECYCLE
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name") or "Light"
        light_type = params.get("light_type", "POINT")
        energy = float(params.get("energy", 1000.0))
        color = params.get("color", [1.0, 1.0, 1.0])
        loc = params.get("location", [4.0, -4.0, 5.0])

        return f"""import bpy
print('NOVA_ACTION_START::create_light')
try:
    light_data = bpy.data.lights.new(name='{name}', type='{light_type}')
    light_data.energy = {energy}
    light_data.color = ({color[0]}, {color[1]}, {color[2]})
    light_obj = bpy.data.objects.new(name='{name}', object_data=light_data)
    light_obj.name = '{name}'
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    
    assert light_obj.name in bpy.data.objects
    assert light_obj.type == 'LIGHT'
    print(f'NOVA_ACTION_SUCCESS::create_light::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::create_light::{{str(e)}}')
"""

    @classmethod
    def _build_delete_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name") or "Light"
        return f"""import bpy
print('NOVA_ACTION_START::delete_light')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_data = light_obj.data
    bpy.data.objects.remove(light_obj, do_unlink=True)
    if light_data.users == 0:
        bpy.data.lights.remove(light_data)
    assert '{name}' not in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::delete_light::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::delete_light::{{str(e)}}')
"""

    @classmethod
    def _build_rename_light(cls, params: Dict[str, Any]) -> str:
        old_name = params.get("light_name") or params.get("name")
        new_name = params.get("new_name", "RenamedLight")
        return f"""import bpy
print('NOVA_ACTION_START::rename_light')
try:
    light_obj = bpy.data.objects.get('{old_name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{old_name}' not found")
    light_obj.name = '{new_name}'
    light_obj.data.name = '{new_name}'
    assert '{new_name}' in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::rename_light::{new_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::rename_light::{{str(e)}}')
"""

    @classmethod
    def _build_duplicate_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        new_name = params.get("new_name") or f"{name}_copy"
        return f"""import bpy
print('NOVA_ACTION_START::duplicate_light')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    new_data = light_obj.data.copy()
    new_obj = light_obj.copy()
    new_obj.data = new_data
    new_obj.name = '{new_name}'
    bpy.context.scene.collection.objects.link(new_obj)
    assert new_obj.name in bpy.data.objects
    print(f'NOVA_ACTION_SUCCESS::duplicate_light::{new_name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::duplicate_light::{{str(e)}}')
"""

    @classmethod
    def _build_get_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::get_light')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light = light_obj.data
    info = f"name={{light_obj.name}}:type={{light.type}}:energy={{light.energy}}:color={{list(light.color)}}"
    print(f'NOVA_ACTION_SUCCESS::get_light::{{info}}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_light::{{str(e)}}')
"""

    @classmethod
    def _build_get_lights(cls, params: Dict[str, Any]) -> str:
        return """import bpy
print('NOVA_ACTION_START::get_lights')
try:
    lights = [o.name for o in bpy.data.objects if o.type == 'LIGHT']
    print(f'NOVA_ACTION_SUCCESS::get_lights::{",".join(lights)}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_lights::{str(e)}')
"""

    # -------------------------------------------------------------------------
    # E. LIGHT TRANSFORM
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_light_location(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        loc = params.get("location", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_light_location')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    print(f'NOVA_ACTION_SUCCESS::set_light_location::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_location::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_rotation(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        rot = params.get("rotation", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_light_rotation')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})
    print(f'NOVA_ACTION_SUCCESS::set_light_rotation::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_rotation::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_transform(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        loc = params.get("location", [0.0, 0.0, 0.0])
        rot = params.get("rotation", [0.0, 0.0, 0.0])
        scale = params.get("scale", [1.0, 1.0, 1.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_light_transform')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})
    light_obj.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})
    light_obj.scale = ({scale[0]}, {scale[1]}, {scale[2]})
    print(f'NOVA_ACTION_SUCCESS::set_light_transform::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_transform::{{str(e)}}')
"""

    @classmethod
    def _build_move_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        delta = params.get("delta", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::move_light')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.location.x += {delta[0]}
    light_obj.location.y += {delta[1]}
    light_obj.location.z += {delta[2]}
    print(f'NOVA_ACTION_SUCCESS::move_light::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::move_light::{{str(e)}}')
"""

    @classmethod
    def _build_rotate_light(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        delta = params.get("delta", [0.0, 0.0, 0.0])
        return f"""import bpy
print('NOVA_ACTION_START::rotate_light')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.rotation_euler.x += {delta[0]}
    light_obj.rotation_euler.y += {delta[1]}
    light_obj.rotation_euler.z += {delta[2]}
    print(f'NOVA_ACTION_SUCCESS::rotate_light::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::rotate_light::{{str(e)}}')
"""

    @classmethod
    def _build_point_light_at(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        target_obj_name = params.get("target_object")
        target_loc = params.get("target_location")

        if target_obj_name:
            target_expr = f"bpy.data.objects.get('{target_obj_name}').location"
        elif target_loc:
            target_expr = f"Vector(({target_loc[0]}, {target_loc[1]}, {target_loc[2]}))"
        else:
            target_expr = "Vector((0.0, 0.0, 0.0))"

        return f"""import bpy
from mathutils import Vector
print('NOVA_ACTION_START::point_light_at')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    target = {target_expr}
    direction = target - light_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    light_obj.rotation_euler = rot_quat.to_euler()
    print(f'NOVA_ACTION_SUCCESS::point_light_at::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::point_light_at::{{str(e)}}')
"""

    # -------------------------------------------------------------------------
    # F. LIGHT TYPES & PROPERTIES
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_light_type(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        light_type = params.get("light_type", "POINT")
        return f"""import bpy
print('NOVA_ACTION_START::set_light_type')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.data.type = '{light_type}'
    print(f'NOVA_ACTION_SUCCESS::set_light_type::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_type::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_energy(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        energy = float(params.get("energy", 1000.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_light_energy')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.data.energy = {energy}
    print(f'NOVA_ACTION_SUCCESS::set_light_energy::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_energy::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_color(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        color = params.get("color", [1.0, 1.0, 1.0])
        return f"""import bpy
print('NOVA_ACTION_START::set_light_color')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.data.color = ({color[0]}, {color[1]}, {color[2]})
    print(f'NOVA_ACTION_SUCCESS::set_light_color::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_color::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_temperature(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        kelvin = float(params.get("temperature", 5500.0))
        rgb = cls.kelvin_to_rgb(kelvin)
        return f"""import bpy
print('NOVA_ACTION_START::set_light_temperature')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light_obj.data.color = ({rgb[0]}, {rgb[1]}, {rgb[2]})
    print(f'NOVA_ACTION_SUCCESS::set_light_temperature::{name}->{kelvin}K')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_temperature::{{str(e)}}')
"""

    @classmethod
    def _build_set_light_size(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        size = float(params.get("size", 1.0))
        return f"""import bpy
print('NOVA_ACTION_START::set_light_size')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    if hasattr(light_obj.data, 'shadow_soft_size'):
        light_obj.data.shadow_soft_size = {size}
    if hasattr(light_obj.data, 'size'):
        light_obj.data.size = {size}
    print(f'NOVA_ACTION_SUCCESS::set_light_size::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_light_size::{{str(e)}}')
"""

    @classmethod
    def _build_set_spot_angle(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        spot_size = float(params.get("spot_size", 45.0))
        if spot_size > 6.28:
            spot_size = math.radians(spot_size)
        return f"""import bpy
print('NOVA_ACTION_START::set_spot_angle')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    if light_obj.data.type != 'SPOT':
        raise ValueError("Light '{name}' is not a SPOT light")
    light_obj.data.spot_size = {spot_size}
    print(f'NOVA_ACTION_SUCCESS::set_spot_angle::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_spot_angle::{{str(e)}}')
"""

    @classmethod
    def _build_set_spot_blend(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        blend = float(params.get("spot_blend", 0.5))
        return f"""import bpy
print('NOVA_ACTION_START::set_spot_blend')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    if light_obj.data.type != 'SPOT':
        raise ValueError("Light '{name}' is not a SPOT light")
    light_obj.data.spot_blend = {blend}
    print(f'NOVA_ACTION_SUCCESS::set_spot_blend::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_spot_blend::{{str(e)}}')
"""

    @classmethod
    def _build_set_shadow_settings(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        use_shadow = params.get("use_shadow")
        soft_size = params.get("shadow_soft_size")

        ops = []
        if use_shadow is not None:
            ops.append(f"if hasattr(light, 'use_shadow'): light.use_shadow = {bool(use_shadow)}")
        if soft_size is not None:
            ops.append(f"if hasattr(light, 'shadow_soft_size'): light.shadow_soft_size = float({soft_size})")

        ops_str = "\n    ".join(ops) if ops else "pass"

        return f"""import bpy
print('NOVA_ACTION_START::set_shadow_settings')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light = light_obj.data
    {ops_str}
    print(f'NOVA_ACTION_SUCCESS::set_shadow_settings::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::set_shadow_settings::{{str(e)}}')
"""

    @classmethod
    def _build_get_light_state(cls, params: Dict[str, Any]) -> str:
        name = params.get("light_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::get_light_state')
try:
    light_obj = bpy.data.objects.get('{name}')
    if not light_obj or light_obj.type != 'LIGHT':
        raise ValueError("Light '{name}' not found")
    light = light_obj.data
    spot_a = light.spot_size if light.type == 'SPOT' else 0.0
    spot_b = light.spot_blend if light.type == 'SPOT' else 0.0
    info = f"name={{light_obj.name}}:type={{light.type}}:energy={{light.energy}}:color={{list(light.color)}}:loc={{list(light_obj.location)}}:spot_angle={{spot_a}}:spot_blend={{spot_b}}"
    print(f'NOVA_ACTION_SUCCESS::get_light_state::{{info}}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_light_state::{{str(e)}}')
"""

    # -------------------------------------------------------------------------
    # G. SCENE LIGHTING / VALIDATION
    # -------------------------------------------------------------------------

    @classmethod
    def _build_get_scene_lighting(cls, params: Dict[str, Any]) -> str:
        return """import bpy
print('NOVA_ACTION_START::get_scene_lighting')
try:
    lights = [f"{o.name}:{o.data.type}:{o.data.energy}" for o in bpy.data.objects if o.type == 'LIGHT']
    cam = bpy.context.scene.camera.name if bpy.context.scene.camera else 'NONE'
    print(f'NOVA_ACTION_SUCCESS::get_scene_lighting::active_camera={cam};lights={",".join(lights)}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::get_scene_lighting::{str(e)}')
"""

    @classmethod
    def _build_validate_camera(cls, params: Dict[str, Any]) -> str:
        name = params.get("camera_name") or params.get("name")
        return f"""import bpy
print('NOVA_ACTION_START::validate_camera')
try:
    cam_obj = bpy.data.objects.get('{name}')
    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError("Camera '{name}' does not exist or is invalid")
    cam = cam_obj.data
    assert cam.lens > 0.0
    assert cam.clip_end > cam.clip_start
    print(f'NOVA_ACTION_SUCCESS::validate_camera::{name}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::validate_camera::{{str(e)}}')
"""

    @classmethod
    def _build_validate_lighting(cls, params: Dict[str, Any]) -> str:
        return """import bpy
print('NOVA_ACTION_START::validate_lighting')
try:
    light_objs = [o for o in bpy.data.objects if o.type == 'LIGHT']
    if not light_objs:
        raise ValueError("No light sources present in scene")
    for l in light_objs:
        assert l.data.energy >= 0.0
    print(f'NOVA_ACTION_SUCCESS::validate_lighting::count={len(light_objs)}')
except Exception as e:
    print(f'NOVA_ACTION_ERROR::validate_lighting::{str(e)}')
"""


SUPPORTED_CAMERA_LIGHTING_ACTIONS: Set[str] = {
    # Camera Lifecycle
    "create_camera", "delete_camera", "rename_camera", "duplicate_camera",
    "get_camera", "get_cameras", "set_active_camera",
    # Camera Transform
    "set_camera_location", "set_camera_rotation", "set_camera_transform",
    "move_camera", "rotate_camera", "point_camera_at", "track_camera_to_object",
    # Camera Optics
    "set_camera_lens", "set_camera_sensor", "set_camera_clip_start", "set_camera_clip_end",
    "set_camera_shift", "set_camera_type", "set_camera_dof", "set_camera_dof_distance",
    "set_camera_dof_object", "get_camera_state",
    # Light Lifecycle
    "create_light", "delete_light", "rename_light", "duplicate_light",
    "get_light", "get_lights",
    # Light Transform
    "set_light_location", "set_light_rotation", "set_light_transform",
    "move_light", "rotate_light", "point_light_at",
    # Light Types & Properties
    "set_light_type", "set_light_energy", "set_light_color", "set_light_temperature",
    "set_light_size", "set_spot_angle", "set_spot_blend", "set_shadow_settings",
    "get_light_state",
    # Scene Lighting & Validation
    "get_scene_lighting", "validate_camera", "validate_lighting"
}
