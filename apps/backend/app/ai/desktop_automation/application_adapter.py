"""Base Application Adapter and Blender Adapter preparation for AI Software Copilot integration.

Establishes canonical application context retrieval, real infrastructure action execution,
and verified state observation without mock success.
"""

from typing import Any, Dict, List, Optional
import time
import structlog

from app.ai.desktop_automation.interfaces import IApplicationAdapter
from app.ai.desktop_automation.models import (
    ApplicationContext,
    ApplicationIdentity,
    ApplicationProfile,
    ApplicationState,
    AutomationAction,
    AutomationResult,
    VerificationResult,
)
from app.ai.desktop_automation.application_profiles import ApplicationProfiles
from app.ai.desktop_automation.security_engine import SecurityEngine
from app.ai.desktop_automation.window_tracker import WindowTracker
from app.ai.desktop_automation.verification_engine import VerificationEngine

logger = structlog.get_logger("application_adapter")


class BaseApplicationAdapter(IApplicationAdapter):
    """Base application adapter for desktop software copilots.

    Enforces SecurityEngine checks before any action logic. Delegates real execution to Nova's
    desktop automation infrastructure and explicitly rejects unsupported/unimplemented actions with success=False.
    """

    SUPPORTED_ACTION_TYPES = {
        "launch",
        "activate_window",
        "click",
        "double_click",
        "right_click",
        "type_text",
        "type",
        "press_key",
        "hotkey",
        "shortcut",
        "open_url",
        "run_terminal_command",
        "file_operation",
        "configure_setting",
    }

    def __init__(self, app_name: str, engine: Optional[Any] = None) -> None:
        self.app_name = app_name
        self.profiles = ApplicationProfiles()
        self.profile: ApplicationProfile = self.profiles.get_profile(app_name)
        self.window_tracker = WindowTracker()
        self.security_engine = SecurityEngine()
        self.verification_engine = VerificationEngine()
        self.engine = engine

    def _is_title_matched(self, title: str) -> bool:
        """Helper to match app_name against window title flexibly."""
        if not title:
            return False
        t_clean = title.lower().replace(" ", "").replace("-", "").replace("_", "")
        a_clean = self.app_name.lower().replace(" ", "").replace("-", "").replace("_", "")
        e_clean = self.profile.executable_name.lower().replace(".exe", "") if self.profile else ""

        if a_clean in t_clean or (e_clean and e_clean in t_clean):
            return True
        if a_clean == "vscode" and ("visualstudiocode" in t_clean or "code" in t_clean):
            return True
        return False

    def get_identity(self) -> Optional[ApplicationIdentity]:
        """Return application identity specification based on real OS window/process inspection."""
        window_info = self.window_tracker.get_active_window_info() or {}
        title = window_info.get("title", "")
        is_matched = self._is_title_matched(title)

        if not is_matched and not window_info.get("process_id"):
            return None

        return ApplicationIdentity(
            app_name=self.app_name,
            bundle_id=self.profile.bundle_id if self.profile else self.app_name,
            executable_name=self.profile.executable_name if self.profile else f"{self.app_name.lower()}.exe",
            executable_path=window_info.get("executable_path") if is_matched else None,
            process_id=window_info.get("process_id") if is_matched else None,
            window_class=None,
            architecture=None,
            is_elevated=False,
        )

    async def detect(self) -> bool:
        """Detect if target application window or process is currently active."""
        window_info = self.window_tracker.get_active_window_info()
        if not window_info or not window_info.get("title"):
            return False
        return self._is_title_matched(window_info.get("title", ""))

    async def get_context(self) -> ApplicationContext:
        """Retrieve real-time application context using WindowTracker and ApplicationProfiles.

        Unavailable fields remain None to enforce zero context hallucination.
        """
        window_info = self.window_tracker.get_active_window_info() or {}
        is_matched = await self.detect()

        return ApplicationContext(
            app_name=self.app_name,
            process_id=window_info.get("process_id") if is_matched else None,
            executable_path=window_info.get("executable_path") if is_matched else None,
            window_title=window_info.get("title") if is_matched else None,
            window_handle=window_info.get("handle") if is_matched else None,
            monitor_info=window_info.get("monitor_info") if is_matched else None,
            profile=self.profile if is_matched else None,
            ui_accessibility_tree=None,
            ocr_vision_data=None,
            recent_activity=[],
            timestamp=time.time(),
        )

    def get_capabilities(self) -> List[str]:
        """Return supported copilot action capabilities."""
        return list(self.profile.control_map.keys())

    def get_action_schema(self, action_type: str) -> Dict[str, Any]:
        """Return validation schema/specification for target action_type."""
        action_clean = action_type.lower()
        if action_clean in self.SUPPORTED_ACTION_TYPES:
            return {
                "action_type": action_clean,
                "supported": True,
                "required_params": ["target_label"] if action_clean in ("click", "activate_window") else [],
                "optional_params": ["value", "selector", "timeout_sec"],
            }
        return {"action_type": action_clean, "supported": False, "required_params": [], "optional_params": []}

    def can_handle_action(self, action: AutomationAction) -> bool:
        """Return True if this adapter supports and can execute the given action."""
        action_type = action.action_type.lower()
        return action_type in self.SUPPORTED_ACTION_TYPES or action_type in self.get_capabilities()

    async def observe(self) -> ApplicationState:
        """Observe real-time state snapshot of the application."""
        identity = self.get_identity()
        is_active = await self.detect()
        context = await self.get_context()

        return ApplicationState(
            identity=identity,
            is_running=bool(identity and identity.process_id),
            is_active=is_active,
            window_title=context.window_title,
            window_bounds=context.monitor_info,
            active_view=None,
            last_observed_at=time.time(),
        )

    async def execute(self, action: AutomationAction) -> AutomationResult:
        """Execute an action through security permission guards and real automation infrastructure."""
        logger.info("Executing application action", app_name=self.app_name, action_type=action.action_type)

        # 1. Security Check FIRST: Enforce approval & security bounds before execution logic
        self.security_engine.enforce_security_check(action.action_type)

        # 2. Check if action type is supported by real execution infrastructure
        if not self.can_handle_action(action):
            logger.warning("Unsupported application action requested", app_name=self.app_name, action_type=action.action_type)
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                output=None,
                error_message=f"Action '{action.action_type}' is not supported or implemented for application adapter '{self.app_name}'.",
                duration_sec=0.0,
            )

        action_type = action.action_type.lower()

        # 3. Instantiate real engine if needed
        if self.engine is None:
            from app.ai.desktop_automation.engine import UniversalDesktopAutomationEngine
            self.engine = UniversalDesktopAutomationEngine()

        # 4. Dispatch to real automation engine based on action_type
        start_time = time.time()
        try:
            if action_type == "launch":
                app_info = await self.engine.launch_app(self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=app_info.is_running,
                    output={"app_name": app_info.name, "is_running": app_info.is_running},
                    duration_sec=time.time() - start_time,
                )
            elif action_type == "activate_window":
                win_info = await self.engine.activate_window(action.target_label or self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=win_info.is_active,
                    output={"title": win_info.title, "is_active": win_info.is_active},
                    duration_sec=time.time() - start_time,
                )
            elif action_type == "click":
                res = await self.engine.click_control(action.target_label, container_window=self.app_name)
                return AutomationResult(
                    action_id=action.action_id,
                    success=res.success,
                    output=res.output,
                    error_message=res.error_message,
                    duration_sec=time.time() - start_time,
                )
            elif action_type in ("type_text", "type"):
                text_to_type = action.value if isinstance(action.value, str) else str(action.value or action.target_label)
                res = await self.engine.type_text(text_to_type)
                return AutomationResult(
                    action_id=action.action_id,
                    success=res.success,
                    output=res.output,
                    error_message=res.error_message,
                    duration_sec=time.time() - start_time,
                )
            elif action_type in ("hotkey", "shortcut"):
                shortcut_keys = self.profile.control_map.get(action.target_label, action.target_label)
                res = await self.engine.keyboard_controller.hotkey(shortcut_keys.split("+")) if hasattr(self.engine, "keyboard_controller") else None
                return AutomationResult(
                    action_id=action.action_id,
                    success=res is not None,
                    output={"hotkey": shortcut_keys},
                    duration_sec=time.time() - start_time,
                )
            else:
                return self.engine.action_executor.execute_action(action)
        except Exception as e:
            logger.error("Real action execution failed", error=str(e))
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                error_message=f"Action execution error: {str(e)}",
                duration_sec=time.time() - start_time,
            )

    async def verify(self, action: AutomationAction, result: AutomationResult) -> VerificationResult:
        """Perform post-execution state verification.

        Verification fails (verified=False, confidence=0.0) if action execution was unsuccessful or unsupported.
        Does NOT trust result.success blindly.
        """
        if not result.success:
            return VerificationResult(
                action_id=action.action_id,
                verified=False,
                method_used="real_state_inspection",
                confidence=0.0,
                details=f"Verification failed: Action '{action.action_type}' execution was unsuccessful ({result.error_message or 'No output'}).",
            )

        observed_state = await self.observe()
        expected = f"Executed {action.action_type} for {self.app_name}"

        return self.verification_engine.verify_action_outcome(
            action.action_id,
            expected,
            observed_state=observed_state,
            method_used="window_tracker_and_real_state",
        )


class BlenderApplicationAdapter(BaseApplicationAdapter):
    """Blender Software Copilot Adapter.

    Provides structured BPY action execution for 3D modeling, material generation, and scene manipulation.
    Rejects arbitrary Python execution and unvalidated parameters with success=False.
    """

    BLENDER_STRUCTURED_ACTIONS = {
        "create_object",
        "delete_object",
        "move_object",
        "transform_object",
        "rename_object",
        "create_material",
        "set_material_properties",
        "select_object",
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


    def __init__(self, engine: Optional[Any] = None) -> None:
        super().__init__("Blender", engine=engine)
        from app.ai.desktop_automation.blender_adapter import BlenderActionValidator, BlenderBpyExecutor

        self.validator = BlenderActionValidator()
        self.bpy_executor = BlenderBpyExecutor()

    def get_capabilities(self) -> List[str]:
        """Returns Blender copilot executable capabilities."""
        base_caps = super().get_capabilities()
        return list(set(base_caps + list(self.BLENDER_STRUCTURED_ACTIONS)))

    def get_action_schema(self, action_type: str) -> Dict[str, Any]:
        """Returns action parameter schema for Blender operations."""
        action_clean = action_type.lower()
        if action_clean in self.BLENDER_STRUCTURED_ACTIONS:
            return {
                "action_type": action_clean,
                "supported": True,
                "requires_validation": True,
                "forbidden_raw_python": True,
            }
        return super().get_action_schema(action_type)

    def can_handle_action(self, action: AutomationAction) -> bool:
        """Returns True if action is a supported Blender structured operation or base action."""
        action_type = action.action_type.lower().replace("blender:", "")
        if action_type in ("raw_python", "eval_python", "blender_bpy_script"):
            return False
        return action_type in self.BLENDER_STRUCTURED_ACTIONS or super().can_handle_action(action)

    async def execute(self, action: AutomationAction) -> AutomationResult:
        """Execute structured Blender operation."""
        # 1. Security Check FIRST
        self.security_engine.enforce_security_check(action.action_type)

        action_type = action.action_type.lower().replace("blender:", "")

        # Reject raw arbitrary Python string execution attempts
        if action_type in ("raw_python", "eval_python", "blender_bpy_script"):
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                error_message="Unrestricted AI-generated Python execution is strictly forbidden for security.",
                duration_sec=0.0,
            )

        if not self.can_handle_action(action):
            logger.warning("Unsupported Blender action requested", action_type=action.action_type)
            return AutomationResult(
                action_id=action.action_id,
                success=False,
                output=None,
                error_message=f"Action '{action.action_type}' is not supported by BlenderApplicationAdapter.",
                duration_sec=0.0,
            )

        # Handle structured Blender operations
        if action_type in self.BLENDER_STRUCTURED_ACTIONS:
            try:
                validated_params = self.validator.validate_action(action)
                validated_params["action_id"] = action.action_id
            except Exception as e:
                return AutomationResult(
                    action_id=action.action_id,
                    success=False,
                    error_message=f"Blender parameter validation failed: {str(e)}",
                    duration_sec=0.0,
                )

            is_running = await self.detect()
            return await self.bpy_executor.execute_bpy(validated_params, is_blender_running=is_running)

        return await super().execute(action)

    async def verify(self, action: AutomationAction, result: AutomationResult) -> VerificationResult:
        """Verify Blender state transition after action execution."""
        if not result.success:
            return VerificationResult(
                action_id=action.action_id,
                verified=False,
                method_used="blender_bpy_verification",
                confidence=0.0,
                details=f"Verification failed: Blender action '{action.action_type}' failed ({result.error_message or 'No execution output'}).",
            )

        observed_state = await self.observe()
        return self.verification_engine.verify_action_outcome(
            action.action_id,
            f"Executed Blender action {action.action_type}",
            observed_state=observed_state,
            method_used="blender_bpy_verification",
        )


class ApplicationAdapterRegistry:
    """Registry resolving target application adapters (e.g. Blender, VS Code, Office).

    Falls back to BaseApplicationAdapter for generic applications without claiming unsupported capabilities.
    """

    _instance: Optional["ApplicationAdapterRegistry"] = None

    @classmethod
    def get_instance(cls) -> "ApplicationAdapterRegistry":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        from app.ai.desktop_automation.photoshop_adapter import PhotoshopApplicationAdapter
        self._adapters: Dict[str, Any] = {
            "blender": BlenderApplicationAdapter,
            "photoshop": PhotoshopApplicationAdapter,
        }

    def register_adapter(self, app_name: str, adapter_factory: Any) -> None:
        """Register adapter factory or class for target app name."""
        self._adapters[app_name.strip().lower()] = adapter_factory

    def register(self, adapter: Any) -> None:
        """Register adapter instance or class."""
        if hasattr(adapter, "app_name"):
            self._adapters[adapter.app_name.strip().lower()] = lambda engine=None, a=adapter: a
        elif hasattr(adapter, "get_identity"):
            identity = adapter.get_identity()
            if identity and identity.app_name:
                self._adapters[identity.app_name.strip().lower()] = lambda engine=None, a=adapter: a

    def get_adapter(self, app_name: str, engine: Optional[Any] = None) -> BaseApplicationAdapter:
        """Returns specialized adapter if registered, otherwise returns BaseApplicationAdapter."""
        clean_name = app_name.strip().lower()
        if clean_name in self._adapters:
            factory = self._adapters[clean_name]
            if hasattr(factory, "execute_action") or (hasattr(factory, "execute") and not isinstance(factory, type)):
                return factory
            if callable(factory):
                try:
                    return factory(engine=engine)
                except TypeError:
                    return factory
            return factory
        return BaseApplicationAdapter(app_name, engine=engine)
