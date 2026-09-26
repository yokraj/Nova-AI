"""Blender Mesh Modeling & BMesh Domain Executor.

Handles template BPY/BMesh script generation for 29 mesh modeling actions:
- create_mesh_object, create_primitive_mesh, convert_object_to_mesh
- add_vertex, add_edge, add_face, delete_vertices, delete_edges, delete_faces
- extrude_region, extrude_vertices, extrude_edges, extrude_faces, inset_faces, subdivide_edges, bevel_edges, dissolve_vertices, dissolve_edges, dissolve_faces, merge_vertices
- select_mesh_elements, deselect_mesh_elements
- recalculate_normals, flip_normals, separate_mesh_parts, join_mesh_objects
- get_mesh_statistics, get_mesh_topology, validate_mesh
"""

from typing import Any, Dict


class BlenderMeshExecutor:
    """Constructs BPY and BMesh script templates for mesh modeling operations."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Returns validated BPY/BMesh script string for specified mesh modeling action."""

        # -------------------------------------------------------------
        # 1. MESH CREATION ACTIONS
        # -------------------------------------------------------------
        if action_type == "create_mesh_object":
            name = params.get("name", "NewMesh")
            col_name = params.get("collection")
            link_col = (
                f"col = bpy.data.collections.get('{col_name}') or bpy.context.scene.collection\ncol.objects.link(obj)\n"
                if col_name
                else "bpy.context.scene.collection.objects.link(obj)\n"
            )
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mesh = bpy.data.meshes.new(name='{name}_Mesh')\n"
                f"obj = bpy.data.objects.new(name='{name}', object_data=mesh)\n"
                + link_col +
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "create_primitive_mesh":
            prim = params.get("primitive", "cube")
            name = params.get("object_name") or params.get("name") or "PrimitiveMesh"
            loc = params.get("location", (0.0, 0.0, 0.0))
            x, y, z = loc[0], loc[1], loc[2]
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
                "bpy.ops.object.select_all(action='DESELECT')\n"
                f"{bpy_op}\n"
                "obj = bpy.context.active_object or (bpy.context.selected_objects[0] if bpy.context.selected_objects else None)\n"
                "if obj:\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                "    obj.select_set(True)\n"
                f"    obj.name = '{name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{prim}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Failed to create primitive {prim}')\n"
            )

        elif action_type == "convert_object_to_mesh":
            name = params.get("object_name") or params.get("name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                "    bpy.ops.object.convert(target='MESH')\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found.')\n"
            )

        # -------------------------------------------------------------
        # 2. VERTEX / EDGE / FACE OPERATIONS
        # -------------------------------------------------------------
        elif action_type == "add_vertex":
            name = params.get("object_name") or params.get("name", "")
            loc = params.get("location", (0.0, 0.0, 0.0))
            x, y, z = loc[0], loc[1], loc[2]
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                f"    v = bm.verts.new(({x}, {y}, {z}))\n"
                "    bm.verts.index_update()\n"
                "    v_idx = v.index\n"
                "    bm.to_mesh(obj.data)\n"
                "    bm.free()\n"
                "    obj.data.update()\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:index={{v_idx}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "add_edge":
            name = params.get("object_name") or params.get("name", "")
            v1_idx = int(params.get("v1", 0))
            v2_idx = int(params.get("v2", 1))
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                f"    if 0 <= {v1_idx} < len(bm.verts) and 0 <= {v2_idx} < len(bm.verts):\n"
                f"        e = bm.edges.new((bm.verts[{v1_idx}], bm.verts[{v2_idx}]))\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Vertex index out of range for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "add_face":
            name = params.get("object_name") or params.get("name", "")
            v_indices = params.get("vertex_indices", [])
            v_str = ",".join(str(int(i)) for i in v_indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                f"    idxs = [{v_str}]\n"
                "    if len(idxs) >= 3 and all(0 <= i < len(bm.verts) for i in idxs):\n"
                "        verts = [bm.verts[i] for i in idxs]\n"
                "        f = bm.faces.new(verts)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Invalid vertex indices for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "delete_vertices":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_verts = [v for v in bm.verts if v.index in idxs]\n"
                "    if target_verts:\n"
                "        bmesh.ops.delete(bm, geom=target_verts, context='VERTS')\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching vertices found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "delete_edges":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.edges.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_edges = [e for e in bm.edges if e.index in idxs]\n"
                "    if target_edges:\n"
                "        bmesh.ops.delete(bm, geom=target_edges, context='EDGES')\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching edges found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "delete_faces":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_faces = [f for f in bm.faces if f.index in idxs]\n"
                "    if target_faces:\n"
                "        bmesh.ops.delete(bm, geom=target_faces, context='FACES')\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching faces found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        # -------------------------------------------------------------
        # 3. EDITING / TOPOLOGY
        # -------------------------------------------------------------
        elif action_type in ("extrude_region", "extrude_faces"):
            name = params.get("object_name") or params.get("name", "")
            distance = float(params.get("distance", 1.0))
            face_indices = params.get("indices") or params.get("face_indices", [])
            f_str = ",".join(str(int(i)) for i in face_indices) if face_indices else ""
            filter_code = (
                f"    idxs = set([{f_str}])\n    target_faces = [f for f in bm.faces if f.index in idxs]\n"
                if f_str
                else "    target_faces = list(bm.faces)\n"
            )
            return (
                "import bpy, bmesh, mathutils\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                + filter_code +
                "    if target_faces:\n"
                "        res = bmesh.ops.extrude_face_region(bm, geom=target_faces)\n"
                "        verts = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]\n"
                "        for v in verts:\n"
                f"            v.co += v.normal * {distance}\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{distance}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No faces found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "extrude_vertices":
            name = params.get("object_name") or params.get("name", "")
            distance = float(params.get("distance", 1.0))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_verts = [v for v in bm.verts if v.index in idxs]\n"
                if i_str
                else "    target_verts = list(bm.verts)\n"
            )
            return (
                "import bpy, bmesh, mathutils\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                + filter_code +
                "    if target_verts:\n"
                "        res = bmesh.ops.extrude_vert_indiv(bm, verts=target_verts)\n"
                "        for v in res['verts']:\n"
                f"            v.co += mathutils.Vector((0, 0, {distance}))\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No vertices found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "extrude_edges":
            name = params.get("object_name") or params.get("name", "")
            distance = float(params.get("distance", 1.0))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_edges = [e for e in bm.edges if e.index in idxs]\n"
                if i_str
                else "    target_edges = list(bm.edges)\n"
            )
            return (
                "import bpy, bmesh, mathutils\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.edges.ensure_lookup_table()\n"
                + filter_code +
                "    if target_edges:\n"
                "        res = bmesh.ops.extrude_edge_only(bm, edges=target_edges)\n"
                "        verts = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]\n"
                "        for v in verts:\n"
                f"            v.co += mathutils.Vector((0, 0, {distance}))\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No edges found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "inset_faces":
            name = params.get("object_name") or params.get("name", "")
            thickness = float(params.get("thickness") or params.get("amount", 0.2))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_faces = [f for f in bm.faces if f.index in idxs]\n"
                if i_str
                else "    target_faces = list(bm.faces)\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                + filter_code +
                "    if target_faces:\n"
                f"        bmesh.ops.inset_individual(bm, faces=target_faces, thickness={thickness})\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{thickness}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No faces found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "subdivide_edges":
            name = params.get("object_name") or params.get("name", "")
            cuts = int(params.get("cuts", 1))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_edges = [e for e in bm.edges if e.index in idxs]\n"
                if i_str
                else "    target_edges = list(bm.edges)\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.edges.ensure_lookup_table()\n"
                + filter_code +
                "    if target_edges:\n"
                f"        bmesh.ops.subdivide_edges(bm, edges=target_edges, cuts={cuts})\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{cuts}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No edges found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "bevel_edges":
            name = params.get("object_name") or params.get("name", "")
            offset = float(params.get("offset") or params.get("width", 0.1))
            segments = int(params.get("segments", 1))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_edges = [e for e in bm.edges if e.index in idxs]\n"
                if i_str
                else "    target_edges = list(bm.edges)\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.edges.ensure_lookup_table()\n"
                + filter_code +
                "    if target_edges:\n"
                f"        bmesh.ops.bevel(bm, geom=target_edges, offset={offset}, segments={segments})\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{offset}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No edges found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "dissolve_vertices":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_verts = [v for v in bm.verts if v.index in idxs]\n"
                "    if target_verts:\n"
                "        bmesh.ops.dissolve_verts(bm, verts=target_verts)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching vertices found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "dissolve_edges":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.edges.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_edges = [e for e in bm.edges if e.index in idxs]\n"
                "    if target_edges:\n"
                "        bmesh.ops.dissolve_edges(bm, edges=target_edges)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching edges found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "dissolve_faces":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                f"    idxs = set([{i_str}])\n"
                "    target_faces = [f for f in bm.faces if f.index in idxs]\n"
                "    if target_faces:\n"
                "        bmesh.ops.dissolve_faces(bm, faces=target_faces)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No matching faces found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "merge_vertices":
            name = params.get("object_name") or params.get("name", "")
            dist = float(params.get("distance", 0.001))
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_verts = [v for v in bm.verts if v.index in idxs]\n"
                if i_str
                else "    target_verts = list(bm.verts)\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                + filter_code +
                "    if target_verts:\n"
                f"        bmesh.ops.remove_doubles(bm, verts=target_verts, dist={dist})\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{dist}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No vertices found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        # -------------------------------------------------------------
        # 4. SELECTION
        # -------------------------------------------------------------
        elif action_type == "select_mesh_elements":
            name = params.get("object_name") or params.get("name", "")
            elem_raw = str(params.get("element_type", "verts")).lower()
            if elem_raw in ("vert", "verts", "vertex", "vertices"):
                elem_type = "verts"
            elif elem_raw in ("edge", "edges"):
                elem_type = "edges"
            elif elem_raw in ("face", "faces"):
                elem_type = "faces"
            else:
                elem_type = "verts"

            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices)
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                "    bm.edges.ensure_lookup_table()\n"
                "    bm.faces.ensure_lookup_table()\n"
                f"    elems = getattr(bm, '{elem_type}')\n"
                f"    idxs = set([{i_str}])\n"
                "    if idxs and not idxs.issubset(set(range(len(elems)))):\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Index out of range for {elem_type}')\n"
                "    else:\n"
                "        for el in elems:\n"
                "            el.select = (el.index in idxs)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{elem_type}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "deselect_mesh_elements":
            name = params.get("object_name") or params.get("name", "")
            elem_raw = str(params.get("element_type", "verts")).lower()
            if elem_raw in ("vert", "verts", "vertex", "vertices"):
                elem_type = "verts"
            elif elem_raw in ("edge", "edges"):
                elem_type = "edges"
            elif elem_raw in ("face", "faces"):
                elem_type = "faces"
            else:
                elem_type = "verts"

            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            code_deselect = (
                f"    idxs = set([{i_str}])\n    for el in elems:\n        if el.index in idxs:\n            el.select = False\n"
                if i_str
                else "    for el in elems:\n        el.select = False\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.verts.ensure_lookup_table()\n"
                "    bm.edges.ensure_lookup_table()\n"
                "    bm.faces.ensure_lookup_table()\n"
                f"    elems = getattr(bm, '{elem_type}')\n"
                + code_deselect +
                "    bm.to_mesh(obj.data)\n"
                "    bm.free()\n"
                "    obj.data.update()\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{elem_type}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        # -------------------------------------------------------------
        # 5. NORMALS & GEOMETRY
        # -------------------------------------------------------------
        elif action_type == "recalculate_normals":
            name = params.get("object_name") or params.get("name", "")
            inside = params.get("inside", False)
            reverse_code = "    if target_faces:\n        bmesh.ops.reverse_faces(bm, faces=target_faces)\n" if inside else ""
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                "    target_faces = list(bm.faces)\n"
                "    if target_faces:\n"
                "        bmesh.ops.recalc_face_normals(bm, faces=target_faces)\n"
                + reverse_code +
                "    bm.to_mesh(obj.data)\n"
                "    bm.free()\n"
                "    obj.data.update()\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "flip_normals":
            name = params.get("object_name") or params.get("name", "")
            indices = params.get("indices", [])
            i_str = ",".join(str(int(i)) for i in indices) if indices else ""
            filter_code = (
                f"    idxs = set([{i_str}])\n    target_faces = [f for f in bm.faces if f.index in idxs]\n"
                if i_str
                else "    target_faces = list(bm.faces)\n"
            )
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm.faces.ensure_lookup_table()\n"
                + filter_code +
                "    if target_faces:\n"
                "        bmesh.ops.reverse_faces(bm, faces=target_faces)\n"
                "        bm.to_mesh(obj.data)\n"
                "        bm.free()\n"
                "        obj.data.update()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "    else:\n"
                "        bm.free()\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::No faces found for {name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "separate_mesh_parts":
            name = params.get("object_name") or params.get("name", "")
            type_sep = params.get("type", "LOOSE")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    obj.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = obj\n"
                f"    bpy.ops.mesh.separate(type='{type_sep}')\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{type_sep}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "join_mesh_objects":
            target = params.get("target_object") or params.get("name", "")
            sources = params.get("source_objects", [])
            s_str = ",".join(f"'{s}'" for s in sources)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"target_obj = bpy.data.objects.get('{target}')\n"
                f"source_names = [{s_str}]\n"
                "source_objs = [bpy.data.objects.get(n) for n in source_names if bpy.data.objects.get(n)]\n"
                "if target_obj and source_objs:\n"
                "    bpy.ops.object.select_all(action='DESELECT')\n"
                "    target_obj.select_set(True)\n"
                "    for s in source_objs:\n"
                "        s.select_set(True)\n"
                "    bpy.context.view_layer.objects.active = target_obj\n"
                "    bpy.ops.object.join()\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{target}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Target or source objects not found.')\n"
            )

        # -------------------------------------------------------------
        # 6. MESH STATE & INSPECTION
        # -------------------------------------------------------------
        elif action_type == "get_mesh_statistics":
            name = params.get("object_name") or params.get("name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    m = obj.data\n"
                "    v_count = len(m.vertices)\n"
                "    e_count = len(m.edges)\n"
                "    f_count = len(m.polygons)\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:verts={{v_count}}:edges={{e_count}}:faces={{f_count}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "get_mesh_topology":
            name = params.get("object_name") or params.get("name", "")
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    m = obj.data\n"
                "    v_coords = [list(v.co) for v in m.vertices]\n"
                "    e_verts = [list(e.vertices) for e in m.edges]\n"
                "    f_verts = [list(f.vertices) for f in m.polygons]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:verts={{len(v_coords)}}:edges={{len(e_verts)}}:faces={{len(f_verts)}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        elif action_type == "validate_mesh":
            name = params.get("object_name") or params.get("name", "")
            return (
                "import bpy, bmesh\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{name}')\n"
                "if obj and obj.type == 'MESH':\n"
                "    is_valid = obj.data.validate(verbose=False)\n"
                "    bm = bmesh.new()\n"
                "    bm.from_mesh(obj.data)\n"
                "    bm_valid = bm.is_valid\n"
                "    bm.free()\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:mesh_clean={{not is_valid}}:bmesh_valid={{bm_valid}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {name} not found or not mesh.')\n"
            )

        raise ValueError(f"Action '{action_type}' not supported by BlenderMeshExecutor.")
