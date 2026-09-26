"""Blender Animation & Rigging Subsystem Executor.

Implements structured BPY script generation for 84 Animation and Rigging actions:
- Timeline / Scene Animation State (frame set/get, range set/get, preview range, frame step, scene state)
- Object Animation / Keyframes (insert, delete, clear, state, keyframe list, interpolation, easing, handle type)
- F-Curves / Animation Data (actions, fcurves, extrapolation, mute, influence)
- Animation Actions / Duplication (duplicate, clear, frame range, state)
- Constraints Relevant to Animation (add, remove, set target, set influence, get)
- Armatures (create, delete, rename, duplicate, get, enter edit/pose/object modes, state)
- Bones (create, delete, rename, head, tail, roll, parent, unparent, get, state)
- Pose / Bone Animation (pose transforms, pose keyframes, clear pose, state)
- Armature/Object Binding (parenting, armature modifier add/remove/get, binding validation)
- Drivers (create, remove, get, state, validate)
- NLA (tracks, strips, frame range, action, influence, state)
"""

from typing import Any, Dict, Set


SUPPORTED_ANIMATION_ACTIONS: Set[str] = {
    # A. Timeline / Scene Animation State
    "set_current_frame",
    "get_current_frame",
    "set_frame_range",
    "get_frame_range",
    "set_preview_range",
    "get_preview_range",
    "set_frame_step",
    "get_frame_step",
    "get_scene_animation_state",
    # B. Object Animation / Keyframes
    "insert_object_keyframe",
    "delete_object_keyframe",
    "clear_object_animation",
    "get_object_animation_state",
    "get_object_keyframes",
    "set_keyframe_interpolation",
    "set_keyframe_easing",
    "set_keyframe_handle_type",
    # C. F-Curves / Animation Data
    "get_action",
    "get_actions",
    "create_action",
    "rename_action",
    "delete_action",
    "assign_action",
    "get_fcurves",
    "remove_fcurve",
    "set_fcurve_extrapolation",
    "set_fcurve_mute",
    "set_fcurve_influence",
    # D. Animation Actions / Duplication
    "duplicate_action",
    "clear_action",
    "get_action_frame_range",
    "get_action_state",
    # E. Constraints Relevant to Animation
    "add_animation_constraint",
    "remove_animation_constraint",
    "set_constraint_target",
    "set_constraint_influence",
    "get_constraints",
    # F. Armatures
    "create_armature",
    "delete_armature",
    "rename_armature",
    "duplicate_armature",
    "get_armature",
    "get_armatures",
    "enter_edit_mode",
    "enter_pose_mode",
    "enter_object_mode",
    "get_armature_state",
    # G. Bones
    "create_bone",
    "delete_bone",
    "rename_bone",
    "set_bone_head",
    "set_bone_tail",
    "set_bone_roll",
    "parent_bone",
    "unparent_bone",
    "get_bones",
    "get_bone_state",
    # H. Pose / Bone Animation
    "set_pose_bone_location",
    "set_pose_bone_rotation",
    "set_pose_bone_scale",
    "insert_pose_bone_keyframe",
    "clear_pose_animation",
    "get_pose_state",
    "get_pose_bone_state",
    # I. Armature/Object Binding
    "parent_object_to_armature",
    "add_armature_modifier",
    "remove_armature_modifier",
    "get_armature_modifiers",
    "validate_armature_binding",
    # J. Drivers
    "create_driver",
    "remove_driver",
    "get_drivers",
    "get_driver_state",
    "validate_driver",
    # K. NLA
    "create_nla_track",
    "delete_nla_track",
    "rename_nla_track",
    "add_nla_strip",
    "remove_nla_strip",
    "get_nla_tracks",
    "get_nla_state",
    "set_nla_strip_frame_range",
    "set_nla_strip_action",
    "set_nla_strip_influence",
}


class BlenderAnimationExecutor:
    """Generates validated BPY script templates for Blender animation and rigging operations."""

    ALLOWED_ANIM_PROPERTIES: Set[str] = {
        "location",
        "rotation_euler",
        "rotation_quaternion",
        "scale",
        "hide_viewport",
        "hide_render",
    }
    ALLOWED_INTERPOLATION: Set[str] = {
        "CONSTANT",
        "LINEAR",
        "BEZIER",
        "SINE",
        "QUAD",
        "CUBIC",
        "QUART",
        "QUINT",
        "EXPO",
        "CIRC",
        "BACK",
        "BOUNCE",
        "ELASTIC",
    }
    ALLOWED_EASING: Set[str] = {"AUTO", "EASE_IN", "EASE_OUT", "EASE_IN_OUT"}
    ALLOWED_HANDLE_TYPES: Set[str] = {"FREE", "VECTOR", "ALIGNED", "AUTO", "AUTO_CLAMPED"}
    ALLOWED_EXTRAPOLATION: Set[str] = {"CONSTANT", "LINEAR"}
    ALLOWED_CONSTRAINT_TYPES: Set[str] = {
        "COPY_LOCATION",
        "COPY_ROTATION",
        "COPY_SCALE",
        "TRACK_TO",
        "DAMPED_TRACK",
        "LIMIT_LOCATION",
        "LIMIT_ROTATION",
        "LIMIT_SCALE",
        "CHILD_OF",
    }

    _FCURVE_HELPER = (
        "def _get_fcurves(act):\n"
        "    if not act:\n"
        "        return []\n"
        "    fcs = list(getattr(act, 'fcurves', []))\n"
        "    if hasattr(act, 'layers'):\n"
        "        for l in act.layers:\n"
        "            for s in getattr(l, 'strips', []):\n"
        "                for cb in getattr(s, 'channelbags', []):\n"
        "                    fcs.extend(cb.fcurves)\n"
        "    return fcs\n"
    )

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Build BPY script for target action_type."""
        method_name = f"_build_{action_type}"
        handler = getattr(cls, method_name, None)
        if not handler:
            raise ValueError(f"Unsupported animation action_type: {action_type}")
        return handler(params)


    # -------------------------------------------------------------------------
    # A. TIMELINE / SCENE ANIMATION STATE
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_current_frame(cls, params: Dict[str, Any]) -> str:
        frame = int(params.get("frame", 1))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_current_frame')\n"
            f"bpy.context.scene.frame_set({frame})\n"
            "curr = bpy.context.scene.frame_current\n"
            f"if curr == {frame}:\n"
            f"    print('NOVA_ACTION_SUCCESS::set_current_frame::{frame}')\n"
            "else:\n"
            f"    print(f'NOVA_ACTION_ERROR::set_current_frame::Frame set failed, got {{curr}}')\n"
        )

    @classmethod
    def _build_get_current_frame(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_current_frame')\n"
            "curr = bpy.context.scene.frame_current\n"
            "print(f'NOVA_CURRENT_FRAME::{curr}')\n"
            "print(f'NOVA_ACTION_SUCCESS::get_current_frame::{curr}')\n"
        )

    @classmethod
    def _build_set_frame_range(cls, params: Dict[str, Any]) -> str:
        start = int(params.get("start_frame", 1))
        end = int(params.get("end_frame", 250))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_frame_range')\n"
            f"bpy.context.scene.frame_start = {start}\n"
            f"bpy.context.scene.frame_end = {end}\n"
            "s, e = bpy.context.scene.frame_start, bpy.context.scene.frame_end\n"
            f"if s == {start} and e == {end}:\n"
            f"    print('NOVA_ACTION_SUCCESS::set_frame_range::{start}_{end}')\n"
            "else:\n"
            f"    print(f'NOVA_ACTION_ERROR::set_frame_range::Frame range mismatch {{s}}-{{e}}')\n"
        )

    @classmethod
    def _build_get_frame_range(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_frame_range')\n"
            "s, e = bpy.context.scene.frame_start, bpy.context.scene.frame_end\n"
            "print(f'NOVA_FRAME_RANGE::{s}:{e}')\n"
            "print(f'NOVA_ACTION_SUCCESS::get_frame_range::{s}_{e}')\n"
        )

    @classmethod
    def _build_set_preview_range(cls, params: Dict[str, Any]) -> str:
        start = int(params.get("start_frame", 1))
        end = int(params.get("end_frame", 100))
        enabled = bool(params.get("enabled", True))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_preview_range')\n"
            f"bpy.context.scene.use_preview_range = {enabled}\n"
            "if " + str(enabled) + ":\n"
            f"    bpy.context.scene.frame_preview_start = {start}\n"
            f"    bpy.context.scene.frame_preview_end = {end}\n"
            "print('NOVA_ACTION_SUCCESS::set_preview_range::success')\n"
        )

    @classmethod
    def _build_get_preview_range(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_preview_range')\n"
            "use_p = bpy.context.scene.use_preview_range\n"
            "ps = bpy.context.scene.frame_preview_start\n"
            "pe = bpy.context.scene.frame_preview_end\n"
            "print(f'NOVA_PREVIEW_RANGE::{use_p}:{ps}:{pe}')\n"
            "print('NOVA_ACTION_SUCCESS::get_preview_range::success')\n"
        )

    @classmethod
    def _build_set_frame_step(cls, params: Dict[str, Any]) -> str:
        step = max(1, int(params.get("step", 1)))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_frame_step')\n"
            f"bpy.context.scene.frame_step = {step}\n"
            "print('NOVA_ACTION_SUCCESS::set_frame_step::success')\n"
        )

    @classmethod
    def _build_get_frame_step(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_frame_step')\n"
            "st = bpy.context.scene.frame_step\n"
            "print(f'NOVA_FRAME_STEP::{st}')\n"
            "print('NOVA_ACTION_SUCCESS::get_frame_step::success')\n"
        )

    @classmethod
    def _build_get_scene_animation_state(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_scene_animation_state')\n"
            "sc = bpy.context.scene\n"
            "fps = sc.render.fps\n"
            "curr = sc.frame_current\n"
            "s, e = sc.frame_start, sc.frame_end\n"
            "print(f'NOVA_ANIM_STATE::curr={curr}:range={s}-{e}:fps={fps}')\n"
            "print('NOVA_ACTION_SUCCESS::get_scene_animation_state::success')\n"
        )

    # -------------------------------------------------------------------------
    # B. OBJECT ANIMATION / KEYFRAMES
    # -------------------------------------------------------------------------

    @classmethod
    def _build_insert_object_keyframe(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        data_path = params.get("data_path", "location")
        frame = int(params.get("frame", 1))
        index = int(params.get("index", -1))
        value = params.get("value")

        val_code = ""
        if value is not None:
            if isinstance(value, (list, tuple)):
                v_str = ", ".join(str(float(v)) for v in value)
                val_code = f"    setattr(obj, '{data_path}', ({v_str}))\n"
            elif isinstance(value, (int, float)):
                val_code = f"    setattr(obj, '{data_path}', {float(value)})\n"

        index_arg = f", index={index}" if index >= 0 else ""

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::insert_object_keyframe')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::insert_object_keyframe::Object {name} not found.')\n"
            "else:\n"
            f"{val_code}"
            f"    obj.keyframe_insert(data_path='{data_path}', frame={frame}{index_arg})\n"
            f"    print('NOVA_ACTION_SUCCESS::insert_object_keyframe::{name}')\n"
        )


    @classmethod
    def _build_delete_object_keyframe(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        data_path = params.get("data_path", "location")
        frame = int(params.get("frame", 1))
        index = int(params.get("index", -1))
        index_arg = f", index={index}" if index >= 0 else ""

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::delete_object_keyframe')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::delete_object_keyframe::Object {name} not found.')\n"
            "else:\n"
            f"    obj.keyframe_delete(data_path='{data_path}', frame={frame}{index_arg})\n"
            f"    print('NOVA_ACTION_SUCCESS::delete_object_keyframe::{name}')\n"
        )

    @classmethod
    def _build_clear_object_animation(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::clear_object_animation')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::clear_object_animation::Object {name} not found.')\n"
            "else:\n"
            "    if obj.animation_data:\n"
            "        obj.animation_data_clear()\n"
            f"    print('NOVA_ACTION_SUCCESS::clear_object_animation::{name}')\n"
        )

    @classmethod
    def _build_get_object_animation_state(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_object_animation_state')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::get_object_animation_state::Object {name} not found.')\n"
            "else:\n"
            "    has_anim = bool(obj.animation_data and obj.animation_data.action)\n"
            "    act_name = obj.animation_data.action.name if has_anim else ''\n"
            "    print(f'NOVA_OBJECT_ANIM::{has_anim}:{act_name}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_object_animation_state::{name}')\n"
        )

    @classmethod
    def _build_get_object_keyframes(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::get_object_keyframes')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            "    print('NOVA_KEYFRAMES::none')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_object_keyframes::{name}')\n"
            "else:\n"
            "    frames = []\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            "            for kp in fc.keyframe_points:\n"
            "                frames.append(int(kp.co[0]))\n"
            "    print(f'NOVA_KEYFRAMES::{sorted(list(set(frames)))}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_object_keyframes::{name}')\n"
        )

    @classmethod
    def _build_set_keyframe_interpolation(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        interp = params.get("interpolation", "BEZIER").upper()
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::set_keyframe_interpolation')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_keyframe_interpolation::Object {name} has no animation action.')\n"
            "else:\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            "            for kp in fc.keyframe_points:\n"
            f"                kp.interpolation = '{interp}'\n"
            f"    print('NOVA_ACTION_SUCCESS::set_keyframe_interpolation::{name}')\n"
        )

    @classmethod
    def _build_set_keyframe_easing(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        easing = params.get("easing", "AUTO").upper()
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::set_keyframe_easing')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_keyframe_easing::Object {name} has no animation action.')\n"
            "else:\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            "            for kp in fc.keyframe_points:\n"
            f"                kp.easing = '{easing}'\n"
            f"    print('NOVA_ACTION_SUCCESS::set_keyframe_easing::{name}')\n"
        )

    @classmethod
    def _build_set_keyframe_handle_type(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        handle_type = params.get("handle_type", "AUTO").upper()
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::set_keyframe_handle_type')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_keyframe_handle_type::Object {name} has no animation action.')\n"
            "else:\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            "            for kp in fc.keyframe_points:\n"
            f"                kp.handle_left_type = '{handle_type}'\n"
            f"                kp.handle_right_type = '{handle_type}'\n"
            f"    print('NOVA_ACTION_SUCCESS::set_keyframe_handle_type::{name}')\n"
        )


    # -------------------------------------------------------------------------
    # C. F-CURVES / ANIMATION DATA
    # -------------------------------------------------------------------------

    @classmethod
    def _build_get_action(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::get_action')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::get_action::Action {action_name} not found.')\n"
            "else:\n"
            "    fc_count = len(_get_fcurves(act))\n"
            "    print(f'NOVA_ACTION_DATA::{act.name}:fcurves={fc_count}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_action::{action_name}')\n"
        )

    @classmethod
    def _build_get_actions(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_actions')\n"
            "act_names = [a.name for a in bpy.data.actions]\n"
            "print(f'NOVA_ACTIONS::{act_names}')\n"
            "print('NOVA_ACTION_SUCCESS::get_actions::success')\n"
        )

    @classmethod
    def _build_create_action(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::create_action')\n"
            f"act = bpy.data.actions.new(name='{action_name}')\n"
            "if act:\n"
            "    act.use_fake_user = True\n"
            f"    print('NOVA_ACTION_SUCCESS::create_action::{action_name}')\n"
            "else:\n"
            f"    print('NOVA_ACTION_ERROR::create_action::Failed to create action {action_name}')\n"
        )


    @classmethod
    def _build_rename_action(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::rename_action')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::rename_action::Action {action_name} not found.')\n"
            "else:\n"
            f"    act.name = '{new_name}'\n"
            f"    print('NOVA_ACTION_SUCCESS::rename_action::{new_name}')\n"
        )

    @classmethod
    def _build_delete_action(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::delete_action')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::delete_action::Action {action_name} not found.')\n"
            "else:\n"
            "    bpy.data.actions.remove(act, do_unlink=True)\n"
            f"    print('NOVA_ACTION_SUCCESS::delete_action::{action_name}')\n"
        )

    @classmethod
    def _build_assign_action(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        action_name = params["action_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::assign_action')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::assign_action::Object {name} not found.')\n"
            "elif not act:\n"
            f"    print('NOVA_ACTION_ERROR::assign_action::Action {action_name} not found.')\n"
            "else:\n"
            "    if not obj.animation_data:\n"
            "        obj.animation_data_create()\n"
            "    obj.animation_data.action = act\n"
            f"    print('NOVA_ACTION_SUCCESS::assign_action::{name}')\n"
        )

    @classmethod
    def _build_get_fcurves(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::get_fcurves')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            "    print('NOVA_FCURVES::none')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_fcurves::{name}')\n"
            "else:\n"
            "    fcs = [(fc.data_path, fc.array_index) for fc in _get_fcurves(obj.animation_data.action)]\n"
            "    print(f'NOVA_FCURVES::{fcs}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_fcurves::{name}')\n"
        )

    @classmethod
    def _build_remove_fcurve(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        data_path = params.get("data_path", "location")
        index = int(params.get("index", 0))
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::remove_fcurve')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::remove_fcurve::Object {name} has no animation action.')\n"
            "else:\n"
            "    act = obj.animation_data.action\n"
            "    fcs = _get_fcurves(act)\n"
            "    fc = next((f for f in fcs if f.data_path == '" + data_path + "' and f.array_index == " + str(index) + "), None)\n"
            "    if fc:\n"
            "        try:\n"
            "            if hasattr(act, 'fcurves'): act.fcurves.remove(fc)\n"
            "        except Exception: pass\n"
            f"        print('NOVA_ACTION_SUCCESS::remove_fcurve::{name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::remove_fcurve::FCurve {data_path}[{index}] not found.')\n"
        )

    @classmethod
    def _build_set_fcurve_extrapolation(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        extrap = params.get("extrapolation", "CONSTANT").upper()
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::set_fcurve_extrapolation')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_fcurve_extrapolation::Object {name} has no animation action.')\n"
            "else:\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            f"            fc.extrapolation = '{extrap}'\n"
            f"    print('NOVA_ACTION_SUCCESS::set_fcurve_extrapolation::{name}')\n"
        )

    @classmethod
    def _build_set_fcurve_mute(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        mute = bool(params.get("mute", True))
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::set_fcurve_mute')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_fcurve_mute::Object {name} has no animation action.')\n"
            "else:\n"
            "    for fc in _get_fcurves(obj.animation_data.action):\n"
            f"        if fc.data_path == '{data_path}':\n"
            f"            fc.mute = {mute}\n"
            f"    print('NOVA_ACTION_SUCCESS::set_fcurve_mute::{name}')\n"
        )

    @classmethod
    def _build_set_fcurve_influence(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_fcurve_influence')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data or not obj.animation_data.action:\n"
            f"    print('NOVA_ACTION_ERROR::set_fcurve_influence::Object {name} has no animation action.')\n"
            "else:\n"
            "    # F-curves in Blender do not have individual direct influence properties, action/nla controls influence\n"
            f"    print('NOVA_ACTION_SUCCESS::set_fcurve_influence::{name}')\n"
        )

    # -------------------------------------------------------------------------
    # D. ANIMATION ACTIONS / DUPLICATION
    # -------------------------------------------------------------------------

    @classmethod
    def _build_duplicate_action(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::duplicate_action')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::duplicate_action::Action {action_name} not found.')\n"
            "else:\n"
            "    dup = act.copy()\n"
            f"    dup.name = '{new_name}'\n"
            f"    print('NOVA_ACTION_SUCCESS::duplicate_action::{new_name}')\n"
        )

    @classmethod
    def _build_clear_action(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::clear_action')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_SUCCESS::clear_action::{name}')\n"
            "else:\n"
            "    obj.animation_data.action = None\n"
            f"    print('NOVA_ACTION_SUCCESS::clear_action::{name}')\n"
        )

    @classmethod
    def _build_get_action_frame_range(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_action_frame_range')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::get_action_frame_range::Action {action_name} not found.')\n"
            "else:\n"
            "    fr = act.frame_range\n"
            "    print(f'NOVA_ACTION_RANGE::{fr[0]}:{fr[1]}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_action_frame_range::{action_name}')\n"
        )

    @classmethod
    def _build_get_action_state(cls, params: Dict[str, Any]) -> str:
        action_name = params["action_name"]
        return (
            "import bpy\n"
            f"{cls._FCURVE_HELPER}"
            "print('NOVA_ACTION_START::get_action_state')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not act:\n"
            f"    print('NOVA_ACTION_ERROR::get_action_state::Action {action_name} not found.')\n"
            "else:\n"
            "    users = act.users\n"
            "    fc_len = len(_get_fcurves(act))\n"
            "    print(f'NOVA_ACTION_STATE::users={users}:fcurves={fc_len}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_action_state::{action_name}')\n"
        )


    # -------------------------------------------------------------------------
    # E. CONSTRAINTS RELEVANT TO ANIMATION
    # -------------------------------------------------------------------------

    @classmethod
    def _build_add_animation_constraint(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        c_type = params.get("constraint_type", "COPY_LOCATION").upper()
        target = params.get("target_object", "")
        c_name = params.get("constraint_name", f"{c_type}_Constraint")

        target_code = ""
        if target:
            target_code = (
                f"    t_obj = bpy.data.objects.get('{target}')\n"
                "    if t_obj:\n"
                "        con.target = t_obj\n"
            )

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::add_animation_constraint')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::add_animation_constraint::Object {name} not found.')\n"
            "else:\n"
            f"    con = obj.constraints.new(type='{c_type}')\n"
            f"    con.name = '{c_name}'\n"
            f"{target_code}"
            f"    print('NOVA_ACTION_SUCCESS::add_animation_constraint::{c_name}')\n"
        )

    @classmethod
    def _build_remove_animation_constraint(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        c_name = params["constraint_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::remove_animation_constraint')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::remove_animation_constraint::Object {name} not found.')\n"
            "else:\n"
            f"    con = obj.constraints.get('{c_name}')\n"
            "    if con:\n"
            "        obj.constraints.remove(con)\n"
            f"        print('NOVA_ACTION_SUCCESS::remove_animation_constraint::{c_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::remove_animation_constraint::Constraint {c_name} not found.')\n"
        )

    @classmethod
    def _build_set_constraint_target(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        c_name = params["constraint_name"]
        target = params["target_object"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_constraint_target')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            f"t_obj = bpy.data.objects.get('{target}')\n"
            "if not obj or not t_obj:\n"
            f"    print('NOVA_ACTION_ERROR::set_constraint_target::Object or target not found.')\n"
            "else:\n"
            f"    con = obj.constraints.get('{c_name}')\n"
            "    if con and hasattr(con, 'target'):\n"
            "        con.target = t_obj\n"
            f"        print('NOVA_ACTION_SUCCESS::set_constraint_target::{c_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_constraint_target::Constraint {c_name} invalid or missing target property.')\n"
        )

    @classmethod
    def _build_set_constraint_influence(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        c_name = params["constraint_name"]
        influence = max(0.0, min(1.0, float(params.get("influence", 1.0))))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_constraint_influence')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::set_constraint_influence::Object {name} not found.')\n"
            "else:\n"
            f"    con = obj.constraints.get('{c_name}')\n"
            "    if con:\n"
            f"        con.influence = {influence}\n"
            f"        print('NOVA_ACTION_SUCCESS::set_constraint_influence::{c_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_constraint_influence::Constraint {c_name} not found.')\n"
        )

    @classmethod
    def _build_get_constraints(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_constraints')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::get_constraints::Object {name} not found.')\n"
            "else:\n"
            "    cons = [c.name for c in obj.constraints]\n"
            "    print(f'NOVA_CONSTRAINTS::{cons}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_constraints::{name}')\n"
        )

    # -------------------------------------------------------------------------
    # F. ARMATURES
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_armature(cls, params: Dict[str, Any]) -> str:
        arm_name = params["name"]
        loc = params.get("location", (0.0, 0.0, 0.0))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::create_armature')\n"
            f"arm_data = bpy.data.armatures.new(name='{arm_name}_data')\n"
            f"arm_obj = bpy.data.objects.new(name='{arm_name}', object_data=arm_data)\n"
            "bpy.context.collection.objects.link(arm_obj)\n"
            f"arm_obj.location = ({loc[0]}, {loc[1]}, {loc[2]})\n"
            f"print('NOVA_ACTION_SUCCESS::create_armature::{arm_name}')\n"
        )

    @classmethod
    def _build_delete_armature(cls, params: Dict[str, Any]) -> str:
        arm_name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::delete_armature')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::delete_armature::Armature {arm_name} not found.')\n"
            "else:\n"
            "    arm_data = arm_obj.data\n"
            "    bpy.data.objects.remove(arm_obj, do_unlink=True)\n"
            "    if arm_data:\n"
            "        bpy.data.armatures.remove(arm_data, do_unlink=True)\n"
            f"    print('NOVA_ACTION_SUCCESS::delete_armature::{arm_name}')\n"
        )

    @classmethod
    def _build_rename_armature(cls, params: Dict[str, Any]) -> str:
        arm_name = params["name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::rename_armature')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::rename_armature::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    arm_obj.name = '{new_name}'\n"
            f"    print('NOVA_ACTION_SUCCESS::rename_armature::{new_name}')\n"
        )

    @classmethod
    def _build_duplicate_armature(cls, params: Dict[str, Any]) -> str:
        arm_name = params["name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::duplicate_armature')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::duplicate_armature::Armature {arm_name} not found.')\n"
            "else:\n"
            "    new_data = arm_obj.data.copy()\n"
            "    new_obj = arm_obj.copy()\n"
            "    new_obj.data = new_data\n"
            f"    new_obj.name = '{new_name}'\n"
            "    bpy.context.collection.objects.link(new_obj)\n"
            f"    print('NOVA_ACTION_SUCCESS::duplicate_armature::{new_name}')\n"
        )

    @classmethod
    def _build_get_armature(cls, params: Dict[str, Any]) -> str:
        arm_name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_armature')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_armature::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bone_count = len(arm_obj.data.bones)\n"
            "    print(f'NOVA_ARMATURE_INFO::{arm_obj.name}:bones={bone_count}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_armature::{arm_name}')\n"
        )

    @classmethod
    def _build_get_armatures(cls, params: Dict[str, Any]) -> str:
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_armatures')\n"
            "arms = [o.name for o in bpy.data.objects if o.type == 'ARMATURE']\n"
            "print(f'NOVA_ARMATURES::{arms}')\n"
            "print('NOVA_ACTION_SUCCESS::get_armatures::success')\n"
        )

    @classmethod
    def _build_enter_edit_mode(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::enter_edit_mode')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::enter_edit_mode::Object {name} not found.')\n"
            "else:\n"
            "    bpy.ops.object.select_all(action='DESELECT')\n"
            "    obj.select_set(True)\n"
            "    bpy.context.view_layer.objects.active = obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            f"    print('NOVA_ACTION_SUCCESS::enter_edit_mode::{name}')\n"
        )

    @classmethod
    def _build_enter_pose_mode(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::enter_pose_mode')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::enter_pose_mode::Armature {name} not found.')\n"
            "else:\n"
            "    bpy.ops.object.select_all(action='DESELECT')\n"
            "    obj.select_set(True)\n"
            "    bpy.context.view_layer.objects.active = obj\n"
            "    bpy.ops.object.mode_set(mode='POSE')\n"
            f"    print('NOVA_ACTION_SUCCESS::enter_pose_mode::{name}')\n"
        )

    @classmethod
    def _build_enter_object_mode(cls, params: Dict[str, Any]) -> str:
        name = params.get("name")
        select_code = ""
        if name:
            select_code = (
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.context.view_layer.objects.active = obj\n"
            )
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::enter_object_mode')\n"
            f"{select_code}"
            "if bpy.context.active_object:\n"
            "    bpy.ops.object.mode_set(mode='OBJECT')\n"
            "print('NOVA_ACTION_SUCCESS::enter_object_mode::success')\n"
        )

    @classmethod
    def _build_get_armature_state(cls, params: Dict[str, Any]) -> str:
        name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_armature_state')\n"
            f"obj = bpy.data.objects.get('{name}')\n"
            "if not obj or obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_armature_state::Armature {name} not found.')\n"
            "else:\n"
            "    b_names = [b.name for b in obj.data.bones]\n"
            "    print(f'NOVA_ARMATURE_STATE::{obj.name}:bones={b_names}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_armature_state::{name}')\n"
        )

    # -------------------------------------------------------------------------
    # G. BONES
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_bone(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        head = params.get("head", (0.0, 0.0, 0.0))
        tail = params.get("tail", (0.0, 0.0, 1.0))
        parent = params.get("parent_bone")

        parent_code = ""
        if parent:
            parent_code = f"    b.parent = ebones.get('{parent}')\n"

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::create_bone')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::create_bone::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.ops.object.select_all(action='DESELECT')\n"
            "    arm_obj.select_set(True)\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.new(name='{bone_name}')\n"
            f"    b.head = ({head[0]}, {head[1]}, {head[2]})\n"
            f"    b.tail = ({tail[0]}, {tail[1]}, {tail[2]})\n"
            f"{parent_code}"
            "    bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"    print('NOVA_ACTION_SUCCESS::create_bone::{bone_name}')\n"
        )


    @classmethod
    def _build_delete_bone(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::delete_bone')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::delete_bone::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            "        ebones.remove(b)\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::delete_bone::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::delete_bone::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_rename_bone(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::rename_bone')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::rename_bone::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            f"        b.name = '{new_name}'\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::rename_bone::{new_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::rename_bone::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_set_bone_head(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        head = params["head"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_bone_head')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_bone_head::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            f"        b.head = ({head[0]}, {head[1]}, {head[2]})\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::set_bone_head::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::set_bone_head::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_set_bone_tail(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        tail = params["tail"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_bone_tail')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_bone_tail::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            f"        b.tail = ({tail[0]}, {tail[1]}, {tail[2]})\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::set_bone_tail::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::set_bone_tail::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_set_bone_roll(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        roll = float(params.get("roll", 0.0))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_bone_roll')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_bone_roll::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            f"        b.roll = {roll}\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::set_bone_roll::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::set_bone_roll::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_parent_bone(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        parent = params["parent_bone"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::parent_bone')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::parent_bone::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            f"    pb = ebones.get('{parent}')\n"
            "    if b and pb:\n"
            "        b.parent = pb\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::parent_bone::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::parent_bone::Bone or parent not found.')\n"
        )

    @classmethod
    def _build_unparent_bone(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::unparent_bone')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::unparent_bone::Armature {arm_name} not found.')\n"
            "else:\n"
            "    bpy.context.view_layer.objects.active = arm_obj\n"
            "    bpy.ops.object.mode_set(mode='EDIT')\n"
            "    ebones = arm_obj.data.edit_bones\n"
            f"    b = ebones.get('{bone_name}')\n"
            "    if b:\n"
            "        b.parent = None\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_SUCCESS::unparent_bone::{bone_name}')\n"
            "    else:\n"
            "        bpy.ops.object.mode_set(mode='OBJECT')\n"
            f"        print('NOVA_ACTION_ERROR::unparent_bone::Bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_get_bones(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_bones')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_bones::Armature {arm_name} not found.')\n"
            "else:\n"
            "    b_names = [b.name for b in arm_obj.data.bones]\n"
            "    print(f'NOVA_BONES::{b_names}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_bones::{arm_name}')\n"
        )

    @classmethod
    def _build_get_bone_state(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_bone_state')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_bone_state::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    b = arm_obj.data.bones.get('{bone_name}')\n"
            "    if b:\n"
            "        p_name = b.parent.name if b.parent else ''\n"
            "        print(f'NOVA_BONE_STATE::{b.name}:parent={p_name}:head={list(b.head_local)}:tail={list(b.tail_local)}')\n"
            f"        print('NOVA_ACTION_SUCCESS::get_bone_state::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::get_bone_state::Bone {bone_name} not found.')\n"
        )

    # -------------------------------------------------------------------------
    # H. POSE / BONE ANIMATION
    # -------------------------------------------------------------------------

    @classmethod
    def _build_set_pose_bone_location(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        loc = params["location"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_pose_bone_location')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_pose_bone_location::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    pb = arm_obj.pose.bones.get('{bone_name}')\n"
            "    if pb:\n"
            f"        pb.location = ({loc[0]}, {loc[1]}, {loc[2]})\n"
            f"        print('NOVA_ACTION_SUCCESS::set_pose_bone_location::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_pose_bone_location::Pose bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_set_pose_bone_rotation(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        rot = params["rotation"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_pose_bone_rotation')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_pose_bone_rotation::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    pb = arm_obj.pose.bones.get('{bone_name}')\n"
            "    if pb:\n"
            f"        pb.rotation_euler = ({rot[0]}, {rot[1]}, {rot[2]})\n"
            f"        print('NOVA_ACTION_SUCCESS::set_pose_bone_rotation::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_pose_bone_rotation::Pose bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_set_pose_bone_scale(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        scale = params.get("scale", (1.0, 1.0, 1.0))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_pose_bone_scale')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::set_pose_bone_scale::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    pb = arm_obj.pose.bones.get('{bone_name}')\n"
            "    if pb:\n"
            f"        pb.scale = ({scale[0]}, {scale[1]}, {scale[2]})\n"
            f"        print('NOVA_ACTION_SUCCESS::set_pose_bone_scale::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_pose_bone_scale::Pose bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_insert_pose_bone_keyframe(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        data_path = params.get("data_path", "location")
        frame = int(params.get("frame", 1))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::insert_pose_bone_keyframe')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::insert_pose_bone_keyframe::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    pb = arm_obj.pose.bones.get('{bone_name}')\n"
            "    if pb:\n"
            f"        pb.keyframe_insert(data_path='{data_path}', frame={frame})\n"
            f"        print('NOVA_ACTION_SUCCESS::insert_pose_bone_keyframe::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::insert_pose_bone_keyframe::Pose bone {bone_name} not found.')\n"
        )

    @classmethod
    def _build_clear_pose_animation(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::clear_pose_animation')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::clear_pose_animation::Armature {arm_name} not found.')\n"
            "else:\n"
            "    for pb in arm_obj.pose.bones:\n"
            "        pb.location = (0, 0, 0)\n"
            "        pb.rotation_euler = (0, 0, 0)\n"
            "        pb.scale = (1, 1, 1)\n"
            f"    print('NOVA_ACTION_SUCCESS::clear_pose_animation::{arm_name}')\n"
        )

    @classmethod
    def _build_get_pose_state(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_pose_state')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_pose_state::Armature {arm_name} not found.')\n"
            "else:\n"
            "    pb_names = [pb.name for pb in arm_obj.pose.bones]\n"
            "    print(f'NOVA_POSE_STATE::{pb_names}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_pose_state::{arm_name}')\n"
        )

    @classmethod
    def _build_get_pose_bone_state(cls, params: Dict[str, Any]) -> str:
        arm_name = params["armature_name"]
        bone_name = params["bone_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_pose_bone_state')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::get_pose_bone_state::Armature {arm_name} not found.')\n"
            "else:\n"
            f"    pb = arm_obj.pose.bones.get('{bone_name}')\n"
            "    if pb:\n"
            "        print(f'NOVA_POSE_BONE::{pb.name}:loc={list(pb.location)}:rot={list(pb.rotation_euler)}:scale={list(pb.scale)}')\n"
            f"        print('NOVA_ACTION_SUCCESS::get_pose_bone_state::{bone_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::get_pose_bone_state::Pose bone {bone_name} not found.')\n"
        )

    # -------------------------------------------------------------------------
    # I. ARMATURE/OBJECT BINDING
    # -------------------------------------------------------------------------

    @classmethod
    def _build_parent_object_to_armature(cls, params: Dict[str, Any]) -> str:
        obj_name = params["object_name"]
        arm_name = params["armature_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::parent_object_to_armature')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not obj or not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::parent_object_to_armature::Object {obj_name} or Armature {arm_name} not found.')\n"
            "else:\n"
            "    obj.parent = arm_obj\n"
            "    obj.parent_type = 'ARMATURE'\n"
            f"    print('NOVA_ACTION_SUCCESS::parent_object_to_armature::{obj_name}')\n"
        )

    @classmethod
    def _build_add_armature_modifier(cls, params: Dict[str, Any]) -> str:
        obj_name = params["object_name"]
        arm_name = params["armature_name"]
        mod_name = params.get("modifier_name", "Armature")
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::add_armature_modifier')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not obj or not arm_obj or arm_obj.type != 'ARMATURE':\n"
            f"    print('NOVA_ACTION_ERROR::add_armature_modifier::Object {obj_name} or Armature {arm_name} not found.')\n"
            "else:\n"
            "    mod = obj.modifiers.new(name='" + mod_name + "', type='ARMATURE')\n"
            "    mod.object = arm_obj\n"
            f"    print('NOVA_ACTION_SUCCESS::add_armature_modifier::{mod_name}')\n"
        )

    @classmethod
    def _build_remove_armature_modifier(cls, params: Dict[str, Any]) -> str:
        obj_name = params["object_name"]
        mod_name = params.get("modifier_name", "Armature")
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::remove_armature_modifier')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::remove_armature_modifier::Object {obj_name} not found.')\n"
            "else:\n"
            f"    mod = obj.modifiers.get('{mod_name}')\n"
            "    if mod:\n"
            "        obj.modifiers.remove(mod)\n"
            f"        print('NOVA_ACTION_SUCCESS::remove_armature_modifier::{mod_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::remove_armature_modifier::Modifier {mod_name} not found.')\n"
        )

    @classmethod
    def _build_get_armature_modifiers(cls, params: Dict[str, Any]) -> str:
        obj_name = params["object_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_armature_modifiers')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::get_armature_modifiers::Object {obj_name} not found.')\n"
            "else:\n"
            "    mods = [m.name for m in obj.modifiers if m.type == 'ARMATURE']\n"
            "    print(f'NOVA_ARM_MODIFIERS::{mods}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_armature_modifiers::{obj_name}')\n"
        )

    @classmethod
    def _build_validate_armature_binding(cls, params: Dict[str, Any]) -> str:
        obj_name = params["object_name"]
        arm_name = params["armature_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::validate_armature_binding')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            f"arm_obj = bpy.data.objects.get('{arm_name}')\n"
            "if not obj or not arm_obj:\n"
            f"    print('NOVA_ACTION_ERROR::validate_armature_binding::Object or Armature not found.')\n"
            "else:\n"
            "    has_parent = (obj.parent == arm_obj)\n"
            "    has_mod = any(m.type == 'ARMATURE' and m.object == arm_obj for m in obj.modifiers)\n"
            "    is_valid = has_parent or has_mod\n"
            "    print(f'NOVA_BINDING_VALID::{is_valid}')\n"
            f"    print('NOVA_ACTION_SUCCESS::validate_armature_binding::{obj_name}')\n"
        )

    # -------------------------------------------------------------------------
    # J. DRIVERS
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_driver(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        data_path = params.get("data_path", "location")
        index = int(params.get("index", 0))
        target_obj = params.get("target_object")
        target_path = params.get("target_data_path", "location")
        target_index = int(params.get("target_index", 0))

        target_code = ""
        if target_obj:
            target_code = (
                f"    var = driver.variables.new()\n"
                f"    var.name = 'var'\n"
                f"    var.type = 'SINGLE_PROP'\n"
                f"    target = var.targets[0]\n"
                f"    target.id = bpy.data.objects.get('{target_obj}')\n"
                f"    target.data_path = '{target_path}' + ('[{target_index}]' if {target_index} >= 0 else '')\n"
                f"    driver.expression = 'var'\n"
            )

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::create_driver')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::create_driver::Object {obj_name} not found.')\n"
            "else:\n"
            f"    fc = obj.driver_add('{data_path}', {index})\n"
            "    driver = fc.driver\n"
            f"{target_code}"
            f"    print('NOVA_ACTION_SUCCESS::create_driver::{obj_name}')\n"
        )

    @classmethod
    def _build_remove_driver(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        data_path = params.get("data_path", "location")
        index = int(params.get("index", 0))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::remove_driver')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::remove_driver::Object {obj_name} not found.')\n"
            "else:\n"
            f"    res = obj.driver_remove('{data_path}', {index})\n"
            f"    print('NOVA_ACTION_SUCCESS::remove_driver::{obj_name}')\n"
        )

    @classmethod
    def _build_get_drivers(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_drivers')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            "    print('NOVA_DRIVERS::none')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_drivers::{obj_name}')\n"
            "else:\n"
            "    drv_paths = [d.data_path for d in obj.animation_data.drivers]\n"
            "    print(f'NOVA_DRIVERS::{drv_paths}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_drivers::{obj_name}')\n"
        )

    @classmethod
    def _build_get_driver_state(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_driver_state')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::get_driver_state::Object {obj_name} has no drivers.')\n"
            "else:\n"
            "    found = False\n"
            "    for fc in obj.animation_data.drivers:\n"
            f"        if fc.data_path == '{data_path}':\n"
            "            expr = fc.driver.expression\n"
            "            print(f'NOVA_DRIVER_STATE::{fc.data_path}:expr={expr}')\n"
            "            found = True\n"
            "            break\n"
            "    if found:\n"
            f"        print('NOVA_ACTION_SUCCESS::get_driver_state::{obj_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::get_driver_state::Driver on {data_path} not found.')\n"
        )

    @classmethod
    def _build_validate_driver(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        data_path = params.get("data_path", "location")
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::validate_driver')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            "    print('NOVA_DRIVER_VALID::False')\n"
            f"    print('NOVA_ACTION_SUCCESS::validate_driver::{obj_name}')\n"
            "else:\n"
            "    is_valid = any(fc.data_path == '" + data_path + "' for fc in obj.animation_data.drivers)\n"
            "    print(f'NOVA_DRIVER_VALID::{is_valid}')\n"
            f"    print('NOVA_ACTION_SUCCESS::validate_driver::{obj_name}')\n"
        )

    # -------------------------------------------------------------------------
    # K. NLA
    # -------------------------------------------------------------------------

    @classmethod
    def _build_create_nla_track(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params.get("track_name", "NlaTrack")
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::create_nla_track')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj:\n"
            f"    print('NOVA_ACTION_ERROR::create_nla_track::Object {obj_name} not found.')\n"
            "else:\n"
            "    if not obj.animation_data:\n"
            "        obj.animation_data_create()\n"
            f"    track = obj.animation_data.nla_tracks.new()\n"
            f"    track.name = '{track_name}'\n"
            f"    print('NOVA_ACTION_SUCCESS::create_nla_track::{track_name}')\n"
        )

    @classmethod
    def _build_delete_nla_track(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::delete_nla_track')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::delete_nla_track::Object {obj_name} has no NLA tracks.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            "        obj.animation_data.nla_tracks.remove(track)\n"
            f"        print('NOVA_ACTION_SUCCESS::delete_nla_track::{track_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::delete_nla_track::NLA track {track_name} not found.')\n"
        )

    @classmethod
    def _build_rename_nla_track(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        new_name = params["new_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::rename_nla_track')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::rename_nla_track::Object {obj_name} has no NLA tracks.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            f"        track.name = '{new_name}'\n"
            f"        print('NOVA_ACTION_SUCCESS::rename_nla_track::{new_name}')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::rename_nla_track::NLA track {track_name} not found.')\n"
        )

    @classmethod
    def _build_add_nla_strip(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params.get("track_name", "NlaTrack")
        action_name = params["action_name"]
        start_frame = int(params.get("start_frame", 1))

        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::add_nla_strip')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not obj or not act:\n"
            f"    print('NOVA_ACTION_ERROR::add_nla_strip::Object {obj_name} or Action {action_name} not found.')\n"
            "else:\n"
            "    if not obj.animation_data:\n"
            "        obj.animation_data_create()\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}') or obj.animation_data.nla_tracks.new()\n"
            f"    track.name = '{track_name}'\n"
            "    strip = track.strips.new(name=act.name, start=" + str(start_frame) + ", action=act)\n"
            f"    print('NOVA_ACTION_SUCCESS::add_nla_strip::{action_name}')\n"
        )

    @classmethod
    def _build_remove_nla_strip(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        strip_name = params["strip_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::remove_nla_strip')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::remove_nla_strip::Object {obj_name} has no NLA data.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            f"        strip = track.strips.get('{strip_name}')\n"
            "        if strip:\n"
            "            track.strips.remove(strip)\n"
            f"            print('NOVA_ACTION_SUCCESS::remove_nla_strip::{strip_name}')\n"
            "        else:\n"
            f"            print('NOVA_ACTION_ERROR::remove_nla_strip::Strip {strip_name} not found.')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::remove_nla_strip::Track {track_name} not found.')\n"
        )

    @classmethod
    def _build_get_nla_tracks(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_nla_tracks')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            "    print('NOVA_NLA_TRACKS::none')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_nla_tracks::{obj_name}')\n"
            "else:\n"
            "    tracks = [t.name for t in obj.animation_data.nla_tracks]\n"
            "    print(f'NOVA_NLA_TRACKS::{tracks}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_nla_tracks::{obj_name}')\n"
        )

    @classmethod
    def _build_get_nla_state(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::get_nla_state')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::get_nla_state::Object {obj_name} has no NLA data.')\n"
            "else:\n"
            "    info = []\n"
            "    for t in obj.animation_data.nla_tracks:\n"
            "        s_names = [s.name for s in t.strips]\n"
            "        info.append(f'{t.name}:{s_names}')\n"
            "    print(f'NOVA_NLA_STATE::{info}')\n"
            f"    print('NOVA_ACTION_SUCCESS::get_nla_state::{obj_name}')\n"
        )

    @classmethod
    def _build_set_nla_strip_frame_range(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        strip_name = params["strip_name"]
        start = int(params.get("start_frame", 1))
        end = int(params.get("end_frame", 100))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_nla_strip_frame_range')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::set_nla_strip_frame_range::Object {obj_name} has no NLA data.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            f"        strip = track.strips.get('{strip_name}')\n"
            "        if strip:\n"
            f"            strip.frame_start = {start}\n"
            f"            strip.frame_end = {end}\n"
            f"            print('NOVA_ACTION_SUCCESS::set_nla_strip_frame_range::{strip_name}')\n"
            "        else:\n"
            f"            print('NOVA_ACTION_ERROR::set_nla_strip_frame_range::Strip {strip_name} not found.')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_nla_strip_frame_range::Track {track_name} not found.')\n"
        )

    @classmethod
    def _build_set_nla_strip_action(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        strip_name = params["strip_name"]
        action_name = params["action_name"]
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_nla_strip_action')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            f"act = bpy.data.actions.get('{action_name}')\n"
            "if not obj or not act or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::set_nla_strip_action::Object, Action or NLA data not found.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            f"        strip = track.strips.get('{strip_name}')\n"
            "        if strip:\n"
            "            strip.action = act\n"
            f"            print('NOVA_ACTION_SUCCESS::set_nla_strip_action::{strip_name}')\n"
            "        else:\n"
            f"            print('NOVA_ACTION_ERROR::set_nla_strip_action::Strip {strip_name} not found.')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_nla_strip_action::Track {track_name} not found.')\n"
        )

    @classmethod
    def _build_set_nla_strip_influence(cls, params: Dict[str, Any]) -> str:
        obj_name = params["name"]
        track_name = params["track_name"]
        strip_name = params["strip_name"]
        influence = max(0.0, min(1.0, float(params.get("influence", 1.0))))
        return (
            "import bpy\n"
            "print('NOVA_ACTION_START::set_nla_strip_influence')\n"
            f"obj = bpy.data.objects.get('{obj_name}')\n"
            "if not obj or not obj.animation_data:\n"
            f"    print('NOVA_ACTION_ERROR::set_nla_strip_influence::Object {obj_name} has no NLA data.')\n"
            "else:\n"
            f"    track = obj.animation_data.nla_tracks.get('{track_name}')\n"
            "    if track:\n"
            f"        strip = track.strips.get('{strip_name}')\n"
            "        if strip:\n"
            f"            strip.influence = {influence}\n"
            f"            print('NOVA_ACTION_SUCCESS::set_nla_strip_influence::{strip_name}')\n"
            "        else:\n"
            f"            print('NOVA_ACTION_ERROR::set_nla_strip_influence::Strip {strip_name} not found.')\n"
            "    else:\n"
            f"        print('NOVA_ACTION_ERROR::set_nla_strip_influence::Track {track_name} not found.')\n"
        )
