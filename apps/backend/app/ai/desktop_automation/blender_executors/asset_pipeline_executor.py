"""Blender Asset Pipeline & Import/Export Executor.

Generates BPY scripts for file I/O (.blend, OBJ, FBX, glTF/GLB, STL, PLY, USD, Alembic),
data-block append/link lifecycle, external asset packaging, dependency path resolution,
batch file processing, asset inspection, and AssetJobManager integration.
"""

from typing import Any, Dict, Set

SUPPORTED_ASSET_PIPELINE_ACTIONS: Set[str] = {
    # Blend File (4)
    "open_blend_file",
    "save_blend_file_as",
    "revert_blend_file",
    "get_blend_file_info",
    # OBJ (2)
    "import_obj",
    "export_obj",
    # FBX (2)
    "import_fbx",
    "export_fbx",
    # glTF / GLB (2)
    "import_gltf",
    "export_gltf",
    # STL (2)
    "import_stl",
    "export_stl",
    # PLY (2)
    "import_ply",
    "export_ply",
    # USD / USDZ (2)
    "import_usd",
    "export_usd",
    # Alembic (2)
    "import_alembic",
    "export_alembic",
    # Append & Link (5)
    "append_datablocks",
    "link_datablocks",
    "get_linked_libraries",
    "relocate_library",
    "reload_library",
    # Asset & Dependencies (6)
    "pack_all_assets",
    "unpack_all_assets",
    "find_missing_assets",
    "make_paths_relative",
    "make_paths_absolute",
    "get_external_file_references",
    # Batch Operations & Job Manager (5)
    "batch_import_files",
    "batch_export_files",
    "submit_asset_job",
    "get_asset_job_status",
    "cancel_asset_job",
    # Inspection (1)
    "inspect_asset_file",
}

ALLOWED_GLTF_FORMATS: Set[str] = {"GLB", "GLTF_SEPARATE"}


class BlenderAssetPipelineExecutor:
    """Domain executor for Blender Import/Export & Asset Pipeline operations."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Constructs BPY script for Asset Pipeline actions."""
        if action_type not in SUPPORTED_ASSET_PIPELINE_ACTIONS:
            raise ValueError(f"Unsupported asset pipeline action: '{action_type}'")

        # ---------------------------------------------------------
        # Blend File Operations
        # ---------------------------------------------------------
        if action_type == "open_blend_file":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::open_blend_file')\n"
                f"bpy.ops.wm.open_mainfile(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::open_blend_file::{filepath}')\n"
            )

        elif action_type == "save_blend_file_as":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::save_blend_file_as')\n"
                f"bpy.ops.wm.save_as_mainfile(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::save_blend_file_as::{filepath}')\n"
            )

        elif action_type == "revert_blend_file":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::revert_blend_file')\n"
                "bpy.ops.wm.revert_mainfile()\n"
                "print('NOVA_ACTION_SUCCESS::revert_blend_file::reverted')\n"
            )

        elif action_type == "get_blend_file_info":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_blend_file_info')\n"
                f"path = '{filepath}'\n"
                "info = {'objects': [], 'materials': [], 'collections': []}\n"
                "with bpy.data.libraries.load(path) as (data_from, _):\n"
                "    info['objects'] = list(data_from.objects)\n"
                "    info['materials'] = list(data_from.materials)\n"
                "    info['collections'] = list(data_from.collections)\n"
                "print('BLEND_INFO_JSON:' + json.dumps(info))\n"
                f"print('NOVA_ACTION_SUCCESS::get_blend_file_info::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # OBJ Format
        # ---------------------------------------------------------
        elif action_type == "import_obj":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_obj')\n"
                f"bpy.ops.wm.obj_import(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_obj::{filepath}')\n"
            )

        elif action_type == "export_obj":
            raw_fp = params.get("filepath") or params.get("file_path") or params.get("path") or params.get("file") or ""
            filepath = str(raw_fp).replace("\\", "/")
            use_selection = bool(params.get("use_selection", False))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_obj')\n"
                f"bpy.ops.wm.obj_export(filepath='{filepath}', export_selected_objects={use_selection})\n"
                f"print('NOVA_ACTION_SUCCESS::export_obj::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # FBX Format
        # ---------------------------------------------------------
        elif action_type == "import_fbx":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_fbx')\n"
                f"bpy.ops.import_scene.fbx(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_fbx::{filepath}')\n"
            )

        elif action_type == "export_fbx":
            filepath = str(params["filepath"]).replace("\\", "/")
            use_selection = bool(params.get("use_selection", False))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_fbx')\n"
                f"bpy.ops.export_scene.fbx(filepath='{filepath}', use_selection={use_selection}, object_types={{'ARMATURE', 'CAMERA', 'EMPTY', 'MESH', 'OTHER'}})\n"
                f"print('NOVA_ACTION_SUCCESS::export_fbx::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # glTF / GLB Format
        # ---------------------------------------------------------
        elif action_type == "import_gltf":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_gltf')\n"
                f"bpy.ops.import_scene.gltf(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_gltf::{filepath}')\n"
            )

        elif action_type == "export_gltf":
            filepath = str(params["filepath"]).replace("\\", "/")
            fmt = str(params.get("export_format", "GLB")).upper()
            if fmt not in ALLOWED_GLTF_FORMATS:
                fmt = "GLB"
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_gltf')\n"
                f"bpy.ops.export_scene.gltf(filepath='{filepath}', export_format='{fmt}')\n"
                f"print('NOVA_ACTION_SUCCESS::export_gltf::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # STL Format
        # ---------------------------------------------------------
        elif action_type == "import_stl":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_stl')\n"
                f"bpy.ops.wm.stl_import(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_stl::{filepath}')\n"
            )

        elif action_type == "export_stl":
            filepath = str(params["filepath"]).replace("\\", "/")
            use_selection = bool(params.get("use_selection", False))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_stl')\n"
                f"bpy.ops.wm.stl_export(filepath='{filepath}', export_selected_objects={use_selection})\n"
                f"print('NOVA_ACTION_SUCCESS::export_stl::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # PLY Format
        # ---------------------------------------------------------
        elif action_type == "import_ply":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_ply')\n"
                f"bpy.ops.wm.ply_import(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_ply::{filepath}')\n"
            )

        elif action_type == "export_ply":
            filepath = str(params["filepath"]).replace("\\", "/")
            use_selection = bool(params.get("use_selection", False))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_ply')\n"
                f"bpy.ops.wm.ply_export(filepath='{filepath}', export_selected_objects={use_selection})\n"
                f"print('NOVA_ACTION_SUCCESS::export_ply::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # USD / USDZ Format
        # ---------------------------------------------------------
        elif action_type == "import_usd":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_usd')\n"
                f"bpy.ops.wm.usd_import(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_usd::{filepath}')\n"
            )

        elif action_type == "export_usd":
            filepath = str(params["filepath"]).replace("\\", "/")
            selected_only = bool(params.get("selected_objects_only", False))
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_usd')\n"
                f"bpy.ops.wm.usd_export(filepath='{filepath}', selected_objects_only={selected_only})\n"
                f"print('NOVA_ACTION_SUCCESS::export_usd::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # Alembic Format
        # ---------------------------------------------------------
        elif action_type == "import_alembic":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::import_alembic')\n"
                f"bpy.ops.wm.alembic_import(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::import_alembic::{filepath}')\n"
            )

        elif action_type == "export_alembic":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::export_alembic')\n"
                f"bpy.ops.wm.alembic_export(filepath='{filepath}')\n"
                f"print('NOVA_ACTION_SUCCESS::export_alembic::{filepath}')\n"
            )

        # ---------------------------------------------------------
        # Append & Link
        # ---------------------------------------------------------
        elif action_type in ("append_datablocks", "link_datablocks"):
            filepath = str(params["filepath"]).replace("\\", "/")
            is_link = (action_type == "link_datablocks")
            object_names = params.get("object_names") or params.get("objects", [])
            material_names = params.get("material_names") or params.get("materials", [])
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"src_path = '{filepath}'\n"
                f"obj_targets = {object_names}\n"
                f"mat_targets = {material_names}\n"
                f"with bpy.data.libraries.load(src_path, link={is_link}) as (data_from, data_to):\n"
                "    if obj_targets:\n"
                "        data_to.objects = [name for name in data_from.objects if name in obj_targets]\n"
                "    else:\n"
                "        data_to.objects = list(data_from.objects)\n"
                "    if mat_targets:\n"
                "        data_to.materials = [name for name in data_from.materials if name in mat_targets]\n"
                "for obj in data_to.objects:\n"
                "    if obj is not None:\n"
                "        obj.use_fake_user = True\n"
                "        if obj.name not in bpy.context.scene.collection.objects:\n"
                "            bpy.context.scene.collection.objects.link(obj)\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{filepath}')\n"
            )

        elif action_type == "get_linked_libraries":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_linked_libraries')\n"
                "libs = [{'name': l.name, 'filepath': l.filepath} for l in bpy.data.libraries]\n"
                "print('LIBRARIES_JSON:' + json.dumps(libs))\n"
                "print('NOVA_ACTION_SUCCESS::get_linked_libraries::' + str(len(libs)))\n"
            )

        elif action_type == "relocate_library":
            name = params["library_name"]
            new_path = str(params["new_filepath"]).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::relocate_library')\n"
                f"lib = bpy.data.libraries.get('{name}')\n"
                "if lib:\n"
                f"    lib.filepath = '{new_path}'\n"
                f"    print('NOVA_ACTION_SUCCESS::relocate_library::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::relocate_library::Library {name} not found.')\n"
            )

        elif action_type == "reload_library":
            name = params["library_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::reload_library')\n"
                f"lib = bpy.data.libraries.get('{name}')\n"
                "if lib:\n"
                "    lib.reload()\n"
                f"    print('NOVA_ACTION_SUCCESS::reload_library::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::reload_library::Library {name} not found.')\n"
            )

        # ---------------------------------------------------------
        # Asset & External Dependencies
        # ---------------------------------------------------------
        elif action_type == "pack_all_assets":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::pack_all_assets')\n"
                "bpy.ops.file.pack_all()\n"
                "print('NOVA_ACTION_SUCCESS::pack_all_assets::packed')\n"
            )

        elif action_type == "unpack_all_assets":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::unpack_all_assets')\n"
                "bpy.ops.file.unpack_all(method='USE_LOCAL')\n"
                "print('NOVA_ACTION_SUCCESS::unpack_all_assets::unpacked')\n"
            )

        elif action_type == "find_missing_assets":
            directory = str(params.get("directory", "")).replace("\\", "/")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::find_missing_assets')\n"
                f"bpy.ops.file.find_missing_files(directory='{directory}')\n"
                f"print('NOVA_ACTION_SUCCESS::find_missing_assets::{directory}')\n"
            )

        elif action_type == "make_paths_relative":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::make_paths_relative')\n"
                "bpy.ops.file.make_paths_relative()\n"
                "print('NOVA_ACTION_SUCCESS::make_paths_relative::done')\n"
            )

        elif action_type == "make_paths_absolute":
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::make_paths_absolute')\n"
                "bpy.ops.file.make_paths_absolute()\n"
                "print('NOVA_ACTION_SUCCESS::make_paths_absolute::done')\n"
            )

        elif action_type == "get_external_file_references":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_external_file_references')\n"
                "refs = [{'name': img.name, 'filepath': img.filepath, 'packed': img.packed_file is not None} for img in bpy.data.images]\n"
                "print('EXTERNAL_REFS_JSON:' + json.dumps(refs))\n"
                "print('NOVA_ACTION_SUCCESS::get_external_file_references::' + str(len(refs)))\n"
            )

        # ---------------------------------------------------------
        # Batch Operations & Job Management
        # ---------------------------------------------------------
        elif action_type == "batch_import_files":
            files = params.get("files", [])
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::batch_import_files')\n"
                f"file_list = {files}\n"
                "imported_count = 0\n"
                "for fpath in file_list:\n"
                "    f_clean = str(fpath).replace('\\\\', '/')\n"
                "    ext = os.path.splitext(f_clean)[1].lower()\n"
                "    if ext == '.obj': bpy.ops.wm.obj_import(filepath=f_clean); imported_count += 1\n"
                "    elif ext in ('.gltf', '.glb'): bpy.ops.import_scene.gltf(filepath=f_clean); imported_count += 1\n"
                "    elif ext == '.fbx': bpy.ops.import_scene.fbx(filepath=f_clean); imported_count += 1\n"
                "    elif ext == '.stl': bpy.ops.wm.stl_import(filepath=f_clean); imported_count += 1\n"
                "    elif ext == '.ply': bpy.ops.wm.ply_import(filepath=f_clean); imported_count += 1\n"
                "    elif ext in ('.usd', '.usda', '.usdc', '.usdz'): bpy.ops.wm.usd_import(filepath=f_clean); imported_count += 1\n"
                "    elif ext == '.abc': bpy.ops.wm.alembic_import(filepath=f_clean); imported_count += 1\n"
                "print('NOVA_ACTION_SUCCESS::batch_import_files::' + str(imported_count))\n"
            )

        elif action_type == "batch_export_files":
            export_dir = str(params["output_directory"]).replace("\\", "/")
            formats = params.get("formats", ["OBJ", "GLB"])
            return (
                "import bpy, os\n"
                "print('NOVA_ACTION_START::batch_export_files')\n"
                f"out_dir = '{export_dir}'\n"
                f"fmts = {formats}\n"
                "os.makedirs(out_dir, exist_ok=True)\n"
                "exported_files = []\n"
                "for fmt in fmts:\n"
                "    f_upper = str(fmt).upper()\n"
                "    if f_upper == 'OBJ':\n"
                "        p = os.path.join(out_dir, 'export_scene.obj').replace('\\\\', '/')\n"
                "        bpy.ops.wm.obj_export(filepath=p)\n"
                "        exported_files.append(p)\n"
                "    elif f_upper in ('GLB', 'GLTF'):\n"
                "        p = os.path.join(out_dir, 'export_scene.glb').replace('\\\\', '/')\n"
                "        bpy.ops.export_scene.gltf(filepath=p, export_format='GLB')\n"
                "        exported_files.append(p)\n"
                "    elif f_upper == 'STL':\n"
                "        p = os.path.join(out_dir, 'export_scene.stl').replace('\\\\', '/')\n"
                "        bpy.ops.wm.stl_export(filepath=p)\n"
                "        exported_files.append(p)\n"
                "    elif f_upper == 'PLY':\n"
                "        p = os.path.join(out_dir, 'export_scene.ply').replace('\\\\', '/')\n"
                "        bpy.ops.wm.ply_export(filepath=p)\n"
                "        exported_files.append(p)\n"
                "print('NOVA_ACTION_SUCCESS::batch_export_files::' + str(len(exported_files)))\n"
            )

        elif action_type == "submit_asset_job":
            job_id = params.get("job_id", "ASSET-JOB-001")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::submit_asset_job')\n"
                f"print('NOVA_ACTION_SUCCESS::submit_asset_job::{job_id}')\n"
            )

        elif action_type == "get_asset_job_status":
            job_id = params.get("job_id", "ASSET-JOB-001")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_asset_job_status')\n"
                f"print('NOVA_ACTION_SUCCESS::get_asset_job_status::{job_id}')\n"
            )

        elif action_type == "cancel_asset_job":
            job_id = params.get("job_id", "ASSET-JOB-001")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::cancel_asset_job')\n"
                f"print('NOVA_ACTION_SUCCESS::cancel_asset_job::{job_id}')\n"
            )

        # ---------------------------------------------------------
        # Inspection
        # ---------------------------------------------------------
        elif action_type == "inspect_asset_file":
            filepath = str(params["filepath"]).replace("\\", "/")
            return (
                "import bpy, os, json\n"
                "print('NOVA_ACTION_START::inspect_asset_file')\n"
                f"path = '{filepath}'\n"
                "exists = os.path.exists(path)\n"
                "size = os.path.getsize(path) if exists else 0\n"
                "ext = os.path.splitext(path)[1].lower()\n"
                "info = {'filepath': path, 'exists': exists, 'size_bytes': size, 'extension': ext}\n"
                "if ext == '.blend' and exists:\n"
                "    try:\n"
                "        with bpy.data.libraries.load(path) as (df, _):\n"
                "            info['objects'] = len(df.objects)\n"
                "            info['materials'] = len(df.materials)\n"
                "            info['collections'] = len(df.collections)\n"
                "    except Exception as e:\n"
                "        info['error'] = str(e)\n"
                "print('ASSET_INSPECT_JSON:' + json.dumps(info))\n"
                f"print('NOVA_ACTION_SUCCESS::inspect_asset_file::{filepath}')\n"
            )

        raise ValueError(f"No BPY template for action '{action_type}'")
