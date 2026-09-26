"""Automation Strategy and Automation Router Abstraction.

Enforces 5-tier automation priority:
Tier 1: Native / Local Application API (e.g. BPY for Blender, IDE APIs)
Tier 2: COM / WebSocket / IPC / CLI (e.g. pywin32 COM, CDP, Playwright)
Tier 3: Windows UI Automation (UIA accessibility tree)
Tier 4: Visual Grounding (OCR / Vision bounding boxes)
Tier 5: Generic Keyboard / Mouse Fallback
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
import structlog

from app.ai.desktop_automation.interfaces import IApplicationAdapter
from app.ai.desktop_automation.models import AutomationAction, AutomationResult

logger = structlog.get_logger("automation_router")


class AutomationTier(int, Enum):
    """Enumerate 5-tier automation execution priority."""

    TIER_1_NATIVE_API = 1
    TIER_2_IPC_COM_CLI = 2
    TIER_3_UI_AUTOMATION = 3
    TIER_4_VISUAL_GROUNDING = 4
    TIER_5_GENERIC_FALLBACK = 5


class RouteDecision(BaseModel):
    """Payload representing a routing strategy decision."""

    tier: AutomationTier = Field(...)
    tier_name: str = Field(...)
    reason: str = Field(...)
    action_type: str = Field(...)
    adapter: Optional[Any] = Field(None)


class AutomationRouter:
    """Evaluates automation actions against application capabilities and selects the highest available tier."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self.registry = registry

    def route_action(self, app_name: str, action: AutomationAction) -> RouteDecision:
        """Helper method resolving target adapter and selecting tier strategy."""
        adapter = None
        if self.registry is not None and hasattr(self.registry, "get_adapter"):
            adapter = self.registry.get_adapter(app_name)
        decision = self.select_strategy(action, adapter=adapter)
        if adapter is not None:
            setattr(decision, "adapter", adapter)
        return decision

    TIER_1_ACTIONS = {
        "create_object",
        "delete_object",
        "move_object",
        "transform_object",
        "rename_object",
        "select_object",
        "create_material",
        "set_material_properties",
        "create_camera",
        "create_light",
        "save_file",
        "blender_save_file",
        "create_scene",
        "delete_scene",
        "rename_scene",
        "set_scene_units",
        "create_collection",
        "delete_collection",
        "rename_collection",
        "link_object_to_collection",
        "unlink_object_from_collection",
        "duplicate_object",
        "hide_object",
        "show_object",
        "apply_transform",
        "parent_object",
        "unparent_object",
        "add_constraint",
        "remove_constraint",
        # Phase 2 Mesh Actions
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
        # Phase 3 Modifier Actions
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
        # Phase 4 Material Actions
        "delete_material",
        "rename_material",
        "get_material",
        "get_materials",
        "assign_material",
        "remove_material",
        "add_material_slot",
        "remove_material_slot",
        "clear_material_slots",
        "get_material_slots",
        "set_principled_base_color",
        "set_principled_metallic",
        "set_principled_roughness",
        "set_principled_ior",
        "set_principled_transmission",
        "set_principled_alpha",
        "set_principled_emission",
        "set_principled_emission_strength",
        "set_principled_normal",
        "create_shader_node",
        "delete_shader_node",
        "rename_shader_node",
        "set_shader_node_property",
        "connect_shader_nodes",
        "disconnect_shader_nodes",
        "get_shader_nodes",
        "get_shader_links",
        "add_noise_texture",
        "add_voronoi_texture",
        "add_wave_texture",
        "add_musgrave_or_noise_equivalent",
        "add_color_ramp",
        "add_mapping_node",
        "add_texture_coordinate_node",
        "add_bump_node",
        "connect_texture_to_material",
        "add_image_texture",
        "set_image_texture_path",
        "set_image_texture_interpolation",
        "set_image_texture_extension",
        "connect_image_texture_to_shader",
        "get_material_state",
        "get_material_node_tree",
        "validate_material",
        "validate_shader_links",
        # Phase 5 Camera & Lighting Actions
        "delete_camera",
        "rename_camera",
        "duplicate_camera",
        "get_camera",
        "get_cameras",
        "set_active_camera",
        "set_camera_location",
        "set_camera_rotation",
        "set_camera_transform",
        "move_camera",
        "rotate_camera",
        "point_camera_at",
        "track_camera_to_object",
        "set_camera_lens",
        "set_camera_sensor",
        "set_camera_clip_start",
        "set_camera_clip_end",
        "set_camera_shift",
        "set_camera_type",
        "set_camera_dof",
        "set_camera_dof_distance",
        "set_camera_dof_object",
        "get_camera_state",
        "delete_light",
        "rename_light",
        "duplicate_light",
        "get_light",
        "get_lights",
        "set_light_location",
        "set_light_rotation",
        "set_light_transform",
        "move_light",
        "rotate_light",
        "point_light_at",
        "set_light_type",
        "set_light_energy",
        "set_light_color",
        "set_light_temperature",
        "set_light_size",
        "set_spot_angle",
        "set_spot_blend",
        "set_shadow_settings",
        "get_light_state",
        "get_scene_lighting",
        "validate_camera",
        "validate_lighting",
        # Phase 6 Animation & Rigging Actions
        "set_current_frame",
        "get_current_frame",
        "set_frame_range",
        "get_frame_range",
        "set_preview_range",
        "get_preview_range",
        "set_frame_step",
        "get_frame_step",
        "get_scene_animation_state",
        "insert_object_keyframe",
        "delete_object_keyframe",
        "clear_object_animation",
        "get_object_animation_state",
        "get_object_keyframes",
        "set_keyframe_interpolation",
        "set_keyframe_easing",
        "set_keyframe_handle_type",
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
        "duplicate_action",
        "clear_action",
        "get_action_frame_range",
        "get_action_state",
        "add_animation_constraint",
        "remove_animation_constraint",
        "set_constraint_target",
        "set_constraint_influence",
        "get_constraints",
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
        "set_pose_bone_location",
        "set_pose_bone_rotation",
        "set_pose_bone_scale",
        "insert_pose_bone_keyframe",
        "clear_pose_animation",
        "get_pose_state",
        "get_pose_bone_state",
        "parent_object_to_armature",
        "add_armature_modifier",
        "remove_armature_modifier",
        "get_armature_modifiers",
        "validate_armature_binding",
        "create_driver",
        "remove_driver",
        "get_drivers",
        "get_driver_state",
        "validate_driver",
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
        # Phase 7 Render & Async Actions
        "get_render_state",
        "get_render_engines",
        "set_render_engine",
        "get_render_engine",
        "set_render_resolution",
        "get_render_resolution",
        "set_render_percentage",
        "get_render_percentage",
        "set_render_frame_range",
        "get_render_frame_range",
        "set_render_file_format",
        "get_render_file_format",
        "set_render_output_path",
        "get_render_output_path",
        "set_render_color_mode",
        "set_render_color_depth",
        "set_render_compression",
        "set_render_transparent",
        "set_render_film_settings",
        "set_render_image_settings",
        "validate_render_settings",
        "set_render_samples",
        "get_render_samples",
        "set_render_denoise",
        "get_render_denoise",
        "set_render_shading_quality",
        "get_render_quality_state",
        "render_still",
        "render_current_frame",
        "render_frame_to_file",
        "render_animation",
        "render_frame_range",
        "render_frame",
        "get_rendered_frames",
        "validate_animation_render_output",
        "submit_render_job",
        "get_render_job",
        "get_render_jobs",
        "get_render_job_status",
        "get_render_job_progress",
        "wait_for_render_job",
        "cancel_render_job",
        "remove_render_job",
        "retry_render_job",
        # Phase 8 Geometry Nodes & Physics Actions
        "create_geometry_node_group",
        "delete_geometry_node_group",
        "rename_geometry_node_group",
        "get_geometry_node_groups",
        "get_geometry_node_group_state",
        "add_geometry_nodes_modifier",
        "remove_geometry_nodes_modifier",
        "assign_geometry_node_group",
        "get_geometry_nodes_modifiers",
        "create_geometry_node",
        "delete_geometry_node",
        "rename_geometry_node",
        "duplicate_geometry_node",
        "get_geometry_nodes",
        "get_geometry_node_state",
        "set_geometry_node_location",
        "set_geometry_node_property",
        "set_geometry_node_input",
        "get_geometry_node_input",
        "get_geometry_node_outputs",
        "connect_geometry_nodes",
        "disconnect_geometry_nodes",
        "get_geometry_node_links",
        "add_geometry_node_socket",
        "remove_geometry_node_socket",
        "add_rigid_body",
        "remove_rigid_body",
        "set_rigid_body_properties",
        "set_rigid_body_mass",
        "set_rigid_body_collision_shape",
        "get_rigid_body_state",
        "configure_rigid_body_world",
        "add_collision_physics",
        "remove_collision_physics",
        "set_collision_properties",
        "get_collision_state",
        "add_cloth_simulation",
        "remove_cloth_simulation",
        "set_cloth_properties",
        "get_cloth_state",
        "add_soft_body_simulation",
        "remove_soft_body_simulation",
        "set_soft_body_properties",
        "get_soft_body_state",
        "add_fluid_simulation",
        "set_fluid_domain",
        "set_fluid_flow",
        "get_fluid_state",
        "add_force_field",
        "remove_force_field",
        "set_force_field_properties",
        "get_force_field_state",
        # Phase 9 Import/Export & Asset Pipeline Actions
        "open_blend_file",
        "save_blend_file_as",
        "revert_blend_file",
        "get_blend_file_info",
        "import_obj",
        "export_obj",
        "import_fbx",
        "export_fbx",
        "import_gltf",
        "export_gltf",
        "import_stl",
        "export_stl",
        "import_ply",
        "export_ply",
        "import_usd",
        "export_usd",
        "import_alembic",
        "export_alembic",
        "append_datablocks",
        "link_datablocks",
        "get_linked_libraries",
        "relocate_library",
        "reload_library",
        "pack_all_assets",
        "unpack_all_assets",
        "find_missing_assets",
        "make_paths_relative",
        "make_paths_absolute",
        "get_external_file_references",
        "batch_import_files",
        "batch_export_files",
        "submit_asset_job",
        "get_asset_job_status",
        "cancel_asset_job",
        "inspect_asset_file",
    }


    TIER_2_ACTIONS = {
        "open_url",
        "fill_form",
        "run_terminal_command",
        "run_browser_playwright",
        "com_execute",
        "office_process",
    }

    TIER_3_ACTIONS = {
        "inspect_accessibility_tree",
        "uia_click",
        "uia_type",
    }

    TIER_4_ACTIONS = {
        "locate_control_visually",
        "extract_screen_text",
        "vision_click",
    }

    def select_strategy(self, action: AutomationAction, adapter: Optional[IApplicationAdapter] = None) -> RouteDecision:
        """Determines the highest priority automation tier for the given action and adapter."""
        action_type = action.action_type.lower()

        # Check Tier 1: Native Application API
        if action_type in self.TIER_1_ACTIONS:
            return RouteDecision(
                tier=AutomationTier.TIER_1_NATIVE_API,
                tier_name="TIER_1_NATIVE_API",
                reason=f"Action '{action.action_type}' uses direct native application API (Tier 1).",
                action_type=action.action_type,
            )

        if adapter is not None:
            capabilities = [c.lower() for c in adapter.get_capabilities()]
            if action_type in capabilities and (
                hasattr(adapter, "BLENDER_STRUCTURED_ACTIONS")
                or hasattr(adapter, "PHOTOSHOP_ACTIONS")
                or (hasattr(adapter, "can_handle_action") and adapter.can_handle_action(action))
            ):
                return RouteDecision(
                    tier=AutomationTier.TIER_1_NATIVE_API,
                    tier_name="TIER_1_NATIVE_API",
                    reason=f"Action '{action.action_type}' is registered in specialized adapter capabilities (Tier 1).",
                    action_type=action.action_type,
                )

        # Check Tier 2: COM / WebSocket / IPC / CLI
        if action_type in self.TIER_2_ACTIONS or "terminal" in action_type or "url" in action_type:
            return RouteDecision(
                tier=AutomationTier.TIER_2_IPC_COM_CLI,
                tier_name="TIER_2_IPC_COM_CLI",
                reason=f"Action '{action.action_type}' uses IPC/COM/CLI protocol (Tier 2).",
                action_type=action.action_type,
            )

        # Check Tier 3: Windows UI Automation
        if action_type in self.TIER_3_ACTIONS or action.selector.get("uia_id") or action.selector.get("control_type"):
            return RouteDecision(
                tier=AutomationTier.TIER_3_UI_AUTOMATION,
                tier_name="TIER_3_UI_AUTOMATION",
                reason=f"Action '{action.action_type}' targets UIA accessibility tree elements (Tier 3).",
                action_type=action.action_type,
            )

        # Check Tier 4: Visual Grounding
        if action_type in self.TIER_4_ACTIONS or action.selector.get("ocr_label") or action.selector.get("vision_prompt"):
            return RouteDecision(
                tier=AutomationTier.TIER_4_VISUAL_GROUNDING,
                tier_name="TIER_4_VISUAL_GROUNDING",
                reason=f"Action '{action.action_type}' uses multimodal visual grounding locator (Tier 4).",
                action_type=action.action_type,
            )

        # Tier 5: Generic Keyboard / Mouse Fallback
        return RouteDecision(
            tier=AutomationTier.TIER_5_GENERIC_FALLBACK,
            tier_name="TIER_5_GENERIC_FALLBACK",
            reason=f"Action '{action.action_type}' uses generic keyboard/mouse fallback (Tier 5).",
            action_type=action.action_type,
        )

    async def route_and_execute(self, action: AutomationAction, adapter: IApplicationAdapter) -> AutomationResult:
        """Evaluates strategy decision and executes action via adapter."""
        decision = self.select_strategy(action, adapter=adapter)
        logger.info("Routing automation action", action_type=action.action_type, tier=decision.tier_name, reason=decision.reason)
        return await adapter.execute(action)
