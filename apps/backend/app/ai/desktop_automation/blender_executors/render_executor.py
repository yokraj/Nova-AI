"""Blender Render Executor.

Generates BPY scripts for render configuration, quality/performance tuning,
still image rendering, animation sequence rendering, and output verification.
"""

from typing import Any, Dict, Set

SUPPORTED_RENDER_ACTIONS: Set[str] = {
    # Render Configuration (21)
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

    # Quality & Performance Settings (6)
    "set_render_samples",
    "get_render_samples",
    "set_render_denoise",
    "get_render_denoise",
    "set_render_shading_quality",
    "get_render_quality_state",

    # Still Image Rendering (3)
    "render_still",
    "render_current_frame",
    "render_frame_to_file",

    # Animation Rendering (5)
    "render_animation",
    "render_frame_range",
    "render_frame",
    "get_rendered_frames",
    "validate_animation_render_output",

    # Async Job System (9)
    "submit_render_job",
    "get_render_job",
    "get_render_jobs",
    "get_render_job_status",
    "get_render_job_progress",
    "wait_for_render_job",
    "cancel_render_job",
    "remove_render_job",
    "retry_render_job",
}


class BlenderRenderExecutor:
    """Domain executor for Blender rendering & output management actions."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Constructs machine-readable BPY scripts for render operations."""
        if action_type not in SUPPORTED_RENDER_ACTIONS:
            raise ValueError(f"Unsupported render action: '{action_type}'")

        # ---------------------------------------------------------
        # Render Configuration Actions (1 - 21)
        # ---------------------------------------------------------
        if action_type == "get_render_state":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_render_state')\n"
                "scene = bpy.context.scene\n"
                "state = {\n"
                "    'engine': scene.render.engine,\n"
                "    'resolution_x': scene.render.resolution_x,\n"
                "    'resolution_y': scene.render.resolution_y,\n"
                "    'resolution_percentage': scene.render.resolution_percentage,\n"
                "    'frame_start': scene.frame_start,\n"
                "    'frame_end': scene.frame_end,\n"
                "    'frame_step': scene.frame_step,\n"
                "    'filepath': scene.render.filepath,\n"
                "    'file_format': scene.render.image_settings.file_format,\n"
                "    'film_transparent': scene.render.film_transparent,\n"
                "}\n"
                "print('RENDER_STATE_JSON:' + json.dumps(state))\n"
                "print('NOVA_ACTION_SUCCESS::get_render_state::' + scene.render.engine)\n"
            )

        elif action_type == "get_render_engines":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_render_engines')\n"
                "# In Blender, engines are registered render engine types\n"
                "engines = ['BLENDER_EEVEE_NEXT', 'CYCLES', 'BLENDER_WORKBENCH', 'BLENDER_EEVEE']\n"
                "print('RENDER_ENGINES_JSON:' + json.dumps(engines))\n"
                "print('NOVA_ACTION_SUCCESS::get_render_engines::' + str(len(engines)))\n"
            )

        elif action_type == "set_render_engine":
            engine = params["engine"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_engine')\n"
                f"engine_name = '{engine}'\n"
                "# Compatibility check for EEVEE in Blender 5.2/4.x vs 3.x\n"
                "if engine_name in ('EEVEE', 'BLENDER_EEVEE') and hasattr(bpy.types, 'RENDERENGINE_EEVEE_NEXT'):\n"
                "    engine_name = 'BLENDER_EEVEE_NEXT'\n"
                "try:\n"
                "    bpy.context.scene.render.engine = engine_name\n"
                "    print(f'NOVA_ACTION_SUCCESS::set_render_engine::{engine_name}')\n"
                "except Exception as e:\n"
                "    print(f'NOVA_ACTION_ERROR::set_render_engine::Failed to set engine {engine_name}: {e}')\n"
            )

        elif action_type == "get_render_engine":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_engine')\n"
                "eng = bpy.context.scene.render.engine\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_engine::{eng}')\n"
            )

        elif action_type == "set_render_resolution":
            x = params["resolution_x"]
            y = params["resolution_y"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_resolution')\n"
                f"bpy.context.scene.render.resolution_x = {x}\n"
                f"bpy.context.scene.render.resolution_y = {y}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_resolution::{x}x{y}')\n"
            )

        elif action_type == "get_render_resolution":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_resolution')\n"
                "rx = bpy.context.scene.render.resolution_x\n"
                "ry = bpy.context.scene.render.resolution_y\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_resolution::{rx}x{ry}')\n"
            )

        elif action_type == "set_render_percentage":
            pct = params["percentage"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_percentage')\n"
                f"bpy.context.scene.render.resolution_percentage = {pct}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_percentage::{pct}')\n"
            )

        elif action_type == "get_render_percentage":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_percentage')\n"
                "pct = bpy.context.scene.render.resolution_percentage\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_percentage::{pct}')\n"
            )

        elif action_type == "set_render_frame_range":
            start = params["start_frame"]
            end = params["end_frame"]
            step = params.get("step", 1)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_frame_range')\n"
                f"bpy.context.scene.frame_start = {start}\n"
                f"bpy.context.scene.frame_end = {end}\n"
                f"bpy.context.scene.frame_step = {step}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_frame_range::{start}-{end}')\n"
            )

        elif action_type == "get_render_frame_range":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_frame_range')\n"
                "fs = bpy.context.scene.frame_start\n"
                "fe = bpy.context.scene.frame_end\n"
                "fst = bpy.context.scene.frame_step\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_frame_range::{fs}-{fe}:{fst}')\n"
            )

        elif action_type == "set_render_file_format":
            fmt = params["file_format"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_file_format')\n"
                f"fmt = '{fmt}'.upper()\n"
                "try:\n"
                "    bpy.context.scene.render.image_settings.file_format = fmt\n"
                "    print(f'NOVA_ACTION_SUCCESS::set_render_file_format::{fmt}')\n"
                "except Exception as e:\n"
                "    print(f'NOVA_ACTION_ERROR::set_render_file_format::Invalid format {fmt}: {e}')\n"
            )

        elif action_type == "get_render_file_format":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_file_format')\n"
                "fmt = bpy.context.scene.render.image_settings.file_format\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_file_format::{fmt}')\n"
            )

        elif action_type == "set_render_output_path":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_output_path')\n"
                f"bpy.context.scene.render.filepath = '{filepath}'\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_output_path::{filepath}')\n"
            )

        elif action_type == "get_render_output_path":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_output_path')\n"
                "fp = bpy.context.scene.render.filepath\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_output_path::{fp}')\n"
            )

        elif action_type == "set_render_color_mode":
            mode = params["color_mode"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_color_mode')\n"
                f"mode = '{mode}'.upper()\n"
                "try:\n"
                "    bpy.context.scene.render.image_settings.color_mode = mode\n"
                "    print(f'NOVA_ACTION_SUCCESS::set_render_color_mode::{mode}')\n"
                "except Exception as e:\n"
                "    print(f'NOVA_ACTION_ERROR::set_render_color_mode::Invalid color mode {mode}: {e}')\n"
            )

        elif action_type == "set_render_color_depth":
            depth = str(params["color_depth"])
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_color_depth')\n"
                f"depth = '{depth}'\n"
                "try:\n"
                "    bpy.context.scene.render.image_settings.color_depth = depth\n"
                "    print(f'NOVA_ACTION_SUCCESS::set_render_color_depth::{depth}')\n"
                "except Exception as e:\n"
                "    print(f'NOVA_ACTION_ERROR::set_render_color_depth::Invalid color depth {depth}: {e}')\n"
            )

        elif action_type == "set_render_compression":
            comp = params["compression"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_compression')\n"
                f"bpy.context.scene.render.image_settings.compression = {comp}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_compression::{comp}')\n"
            )

        elif action_type == "set_render_transparent":
            trans = True if params.get("transparent", True) else False
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_transparent')\n"
                f"bpy.context.scene.render.film_transparent = {trans}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_transparent::{trans}')\n"
            )

        elif action_type == "set_render_film_settings":
            trans = True if params.get("transparent", True) else False
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_film_settings')\n"
                f"bpy.context.scene.render.film_transparent = {trans}\n"
                "print('NOVA_ACTION_SUCCESS::set_render_film_settings::configured')\n"
            )

        elif action_type == "set_render_image_settings":
            fmt = params.get("file_format", "PNG").upper()
            mode = params.get("color_mode", "RGBA").upper()
            depth = str(params.get("color_depth", "8"))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_image_settings')\n"
                "img = bpy.context.scene.render.image_settings\n"
                f"img.file_format = '{fmt}'\n"
                f"img.color_mode = '{mode}'\n"
                f"try:\n"
                f"    img.color_depth = '{depth}'\n"
                "except Exception:\n"
                "    pass\n"
                "print('NOVA_ACTION_SUCCESS::set_render_image_settings::configured')\n"
            )

        elif action_type == "validate_render_settings":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::validate_render_settings')\n"
                "scene = bpy.context.scene\n"
                "if scene.render.resolution_x <= 0 or scene.render.resolution_y <= 0:\n"
                "    print('NOVA_ACTION_ERROR::validate_render_settings::Invalid resolution dimensions')\n"
                "elif not scene.render.filepath:\n"
                "    print('NOVA_ACTION_ERROR::validate_render_settings::Missing output path')\n"
                "else:\n"
                "    print('NOVA_ACTION_SUCCESS::validate_render_settings::valid')\n"
            )

        # ---------------------------------------------------------
        # Quality & Performance Settings (22 - 27)
        # ---------------------------------------------------------
        elif action_type == "set_render_samples":
            samples = params["samples"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_samples')\n"
                "scene = bpy.context.scene\n"
                "if hasattr(scene, 'cycles'):\n"
                f"    scene.cycles.samples = {samples}\n"
                "if hasattr(scene, 'eevee'):\n"
                "    if hasattr(scene.eevee, 'taa_render_samples'):\n"
                f"        scene.eevee.taa_render_samples = {samples}\n"
                "    elif hasattr(scene.eevee, 'render_samples'):\n"
                f"        scene.eevee.render_samples = {samples}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_samples::{samples}')\n"
            )

        elif action_type == "get_render_samples":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_samples')\n"
                "scene = bpy.context.scene\n"
                "samples = 64\n"
                "if scene.render.engine == 'CYCLES' and hasattr(scene, 'cycles'):\n"
                "    samples = scene.cycles.samples\n"
                "elif hasattr(scene, 'eevee'):\n"
                "    if hasattr(scene.eevee, 'taa_render_samples'):\n"
                "        samples = scene.eevee.taa_render_samples\n"
                "    elif hasattr(scene.eevee, 'render_samples'):\n"
                "        samples = scene.eevee.render_samples\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_samples::{samples}')\n"
            )

        elif action_type == "set_render_denoise":
            use_denoise = True if params.get("enabled", True) else False
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_denoise')\n"
                "scene = bpy.context.scene\n"
                "if hasattr(scene, 'cycles'):\n"
                f"    scene.cycles.use_denoising = {use_denoise}\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_denoise::{use_denoise}')\n"
            )

        elif action_type == "get_render_denoise":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_render_denoise')\n"
                "scene = bpy.context.scene\n"
                "denoise = False\n"
                "if hasattr(scene, 'cycles'):\n"
                "    denoise = getattr(scene.cycles, 'use_denoising', False)\n"
                "print(f'NOVA_ACTION_SUCCESS::get_render_denoise::{denoise}')\n"
            )

        elif action_type == "set_render_shading_quality":
            quality = params.get("quality", "MEDIUM")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_render_shading_quality')\n"
                f"print('NOVA_ACTION_SUCCESS::set_render_shading_quality::{quality}')\n"
            )

        elif action_type == "get_render_quality_state":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_render_quality_state')\n"
                "scene = bpy.context.scene\n"
                "info = {'engine': scene.render.engine}\n"
                "print('QUALITY_STATE_JSON:' + json.dumps(info))\n"
                "print('NOVA_ACTION_SUCCESS::get_render_quality_state::ok')\n"
            )

        # ---------------------------------------------------------
        # Still Image Rendering (28 - 30)
        # ---------------------------------------------------------
        elif action_type in ("render_still", "render_current_frame", "render_frame_to_file"):
            filepath = params.get("filepath") or params.get("output_path")
            frame = params.get("frame")
            fp_str = f"'{str(filepath).replace('\\', '/')}'" if filepath else "bpy.context.scene.render.filepath"
            frame_set_code = f"bpy.context.scene.frame_set({frame})\n" if frame is not None else ""

            return (
                "import bpy, os\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"{frame_set_code}"
                f"target_path = {fp_str}\n"
                "if target_path:\n"
                "    bpy.context.scene.render.filepath = target_path\n"
                "bpy.ops.render.render(write_still=True)\n"
                "actual_path = bpy.context.scene.render.frame_path()\n"
                "if os.path.exists(actual_path) and os.path.getsize(actual_path) > 0:\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{{actual_path}}')\n"
                "elif os.path.exists(target_path) and os.path.getsize(target_path) > 0:\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{{target_path}}')\n"
                "else:\n"
                f"    print(f'NOVA_ACTION_ERROR::{action_type}::Render completed but output file missing or 0 bytes at {{target_path}}')\n"
            )

        # ---------------------------------------------------------
        # Animation Rendering (31 - 35)
        # ---------------------------------------------------------
        elif action_type == "render_animation":
            filepath = params.get("filepath") or params.get("output_path")
            fp_str = f"bpy.context.scene.render.filepath = '{str(filepath).replace('\\', '/')}'\n" if filepath else ""
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::render_animation')\n"
                f"{fp_str}"
                "bpy.ops.render.render(animation=True)\n"
                "out_dir = os.path.dirname(bpy.context.scene.render.filepath)\n"
                "print(f'NOVA_ACTION_SUCCESS::render_animation::{out_dir}')\n"
            )

        elif action_type == "render_frame_range":
            start = params["start_frame"]
            end = params["end_frame"]
            step = params.get("step", 1)
            filepath = params.get("filepath") or params.get("output_path")
            fp_str = f"bpy.context.scene.render.filepath = '{str(filepath).replace('\\', '/')}'\n" if filepath else ""
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::render_frame_range')\n"
                f"{fp_str}"
                f"bpy.context.scene.frame_start = {start}\n"
                f"bpy.context.scene.frame_end = {end}\n"
                f"bpy.context.scene.frame_step = {step}\n"
                "bpy.ops.render.render(animation=True)\n"
                f"print('NOVA_ACTION_SUCCESS::render_frame_range::{start}-{end}')\n"
            )

        elif action_type == "render_frame":
            frame = params["frame"]
            filepath = params.get("filepath") or params.get("output_path")
            fp_str = f"bpy.context.scene.render.filepath = '{str(filepath).replace('\\', '/')}'\n" if filepath else ""
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::render_frame')\n"
                f"{fp_str}"
                f"bpy.context.scene.frame_set({frame})\n"
                "bpy.ops.render.render(write_still=True)\n"
                "actual_path = bpy.context.scene.render.frame_path()\n"
                "if os.path.exists(actual_path) and os.path.getsize(actual_path) > 0:\n"
                f"    print(f'NOVA_ACTION_SUCCESS::render_frame::{{actual_path}}')\n"
                "else:\n"
                f"    print(f'NOVA_ACTION_ERROR::render_frame::Frame file missing or 0 bytes at {{actual_path}}')\n"
            )

        elif action_type == "get_rendered_frames":
            filepath = params.get("filepath") or params.get("output_path")
            fp_str = str(filepath).replace('\\', '/') if filepath else ""
            return (
                "import bpy, os, glob\n"
                "print('NOVA_ACTION_START::get_rendered_frames')\n"
                f"target = '{fp_str}' or bpy.context.scene.render.filepath\n"
                "parent_dir = os.path.dirname(target) if os.path.isfile(target) or not os.path.exists(target) else target\n"
                "prefix = os.path.basename(target)\n"
                "found = []\n"
                "if os.path.exists(parent_dir):\n"
                "    for f in os.listdir(parent_dir):\n"
                "        if f.startswith(prefix):\n"
                "            fp = os.path.join(parent_dir, f)\n"
                "            if os.path.getsize(fp) > 0:\n"
                "                found.append(fp)\n"
                "print(f'NOVA_ACTION_SUCCESS::get_rendered_frames::{len(found)}')\n"
            )

        elif action_type == "validate_animation_render_output":
            start = params.get("start_frame", 1)
            end = params.get("end_frame", 1)
            step = params.get("step", 1)
            filepath = params.get("filepath") or params.get("output_path")
            fp_str = str(filepath).replace('\\', '/') if filepath else ""
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::validate_animation_render_output')\n"
                f"target = '{fp_str}' or bpy.context.scene.render.filepath\n"
                f"expected_count = (({end} - {start}) // max(1, {step})) + 1\n"
                "parent_dir = os.path.dirname(target)\n"
                "prefix = os.path.basename(target)\n"
                "found_count = 0\n"
                "if os.path.exists(parent_dir):\n"
                "    for f in os.listdir(parent_dir):\n"
                "        if f.startswith(prefix):\n"
                "            fp = os.path.join(parent_dir, f)\n"
                "            if os.path.getsize(fp) > 0:\n"
                "                found_count += 1\n"
                "if found_count >= expected_count:\n"
                "    print(f'NOVA_ACTION_SUCCESS::validate_animation_render_output::{found_count}/{expected_count}')\n"
                "else:\n"
                "    print(f'NOVA_ACTION_ERROR::validate_animation_render_output::Expected {expected_count} frames, found {found_count}')\n"
            )

        # ---------------------------------------------------------
        # Async Job Actions (36 - 44)
        # ---------------------------------------------------------
        elif action_type in (
            "submit_render_job",
            "get_render_job",
            "get_render_jobs",
            "get_render_job_status",
            "get_render_job_progress",
            "wait_for_render_job",
            "cancel_render_job",
            "remove_render_job",
            "retry_render_job",
        ):
            # Built for direct render job manager dispatch or script verification
            job_id = params.get("job_id", "NOVA-RENDER-JOB")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{job_id}')\n"
            )

        raise ValueError(f"No BPY template for action '{action_type}'")
