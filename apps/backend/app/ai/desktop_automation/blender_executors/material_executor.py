"""Blender Material and Shader Node Executor.

Implements structured material lifecycle, slot assignment, Principled BSDF settings,
shader node graph manipulation, procedural texture nodes, image textures, and node tree inspection.
"""

from typing import Any, Dict, Set


class BlenderMaterialExecutor:
    """Generates validated BPY script templates for Blender material and shading operations."""

    ALLOWED_NODE_TYPES: Set[str] = {
        "ShaderNodeBsdfPrincipled",
        "ShaderNodeOutputMaterial",
        "ShaderNodeTexNoise",
        "ShaderNodeTexVoronoi",
        "ShaderNodeTexWave",
        "ShaderNodeValToRGB",  # ColorRamp
        "ShaderNodeMapping",
        "ShaderNodeTexCoord",
        "ShaderNodeBump",
        "ShaderNodeTexImage",
        "ShaderNodeNormalMap",
        "ShaderNodeMath",
        "ShaderNodeVectorMath",
        "ShaderNodeMix",
        "ShaderNodeMixRGB",
    }

    ALLOWED_INTERPOLATIONS: Set[str] = {"Linear", "Closest", "Cubic", "Smart"}
    ALLOWED_EXTENSIONS: Set[str] = {"Repeat", "Extend", "Clip", "Mirror"}

    @classmethod
    def sanitize_str(cls, val: str) -> str:
        """Sanitizes user input string for BPY code generation."""
        if not val:
            return ""
        return str(val).replace("\\", "/").replace("'", "\\'").replace('"', '\\"')

    @classmethod
    def build_bpy_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Constructs safe BPY Python script for material action."""
        name = cls.sanitize_str(params.get("material_name") or params.get("name", "Material"))
        obj_name = cls.sanitize_str(params.get("object_name") or params.get("target_label", "Cube"))

        # Common BPY helper definitions included in script header
        header = (
            "import bpy\n"
            "import os\n"
            "def _get_mat(mat_name):\n"
            "    return bpy.data.materials.get(mat_name)\n"
            "def _get_node(mat, node_name):\n"
            "    if mat and mat.use_nodes and mat.node_tree:\n"
            "        return mat.node_tree.nodes.get(node_name)\n"
            "    return None\n"
            "def _get_principled(mat):\n"
            "    if mat and mat.use_nodes and mat.node_tree:\n"
            "        return next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)\n"
            "    return None\n"
            "def _set_socket(node, socket_keys, value):\n"
            "    if not node:\n"
            "        return False\n"
            "    for key in socket_keys:\n"
            "        if key in node.inputs:\n"
            "            node.inputs[key].default_value = value\n"
            "            return True\n"
            "    cl_keys = [k.lower().replace(' ', '').replace('_', '') for k in socket_keys]\n"
            "    for inp in node.inputs:\n"
            "        ic = inp.name.lower().replace(' ', '').replace('_', '')\n"
            "        if ic in cl_keys or any(k in ic for k in cl_keys):\n"
            "            inp.default_value = value\n"
            "            return True\n"
            "    return False\n"
        )

        # A. MATERIAL LIFECYCLE
        if action_type == "create_material":
            use_nodes = bool(params.get("use_nodes", True))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}') or bpy.data.materials.new(name='{name}')\n"
                f"mat.use_nodes = {use_nodes}\n"
                "mat.use_fake_user = True\n"
                f"print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
            )

        elif action_type == "delete_material":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat:\n"
                "    bpy.data.materials.remove(mat)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "rename_material":
            new_name = cls.sanitize_str(params.get("new_name", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat:\n"
                f"    mat.name = '{new_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{new_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "get_material":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat:\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:use_nodes={{mat.use_nodes}}:users={{mat.users}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "get_materials":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                "mats = [m.name for m in bpy.data.materials]\n"
                f"print(f'NOVA_ACTION_SUCCESS::{action_type}::count={{len(mats)}}:mats={{mats}}')\n"
            )

        # B. MATERIAL ASSIGNMENT / SLOTS
        elif action_type == "assign_material":
            slot_idx = int(params.get("slot_index", 0))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                f"mat = _get_mat('{name}')\n"
                "if obj and mat:\n"
                "    if not obj.data.materials:\n"
                "        obj.data.materials.append(mat)\n"
                "    else:\n"
                f"        if {slot_idx} < len(obj.data.materials):\n"
                f"            obj.data.materials[{slot_idx}] = mat\n"
                "        else:\n"
                "            obj.data.materials.append(mat)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} or Material {name} not found.')\n"
            )

        elif action_type == "remove_material":
            slot_idx = int(params.get("slot_index", 0))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                f"    if {slot_idx} < len(obj.data.materials):\n"
                f"        obj.data.materials[{slot_idx}] = None\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{slot_idx}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Slot index {slot_idx} out of range on {obj_name}.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} not found.')\n"
            )

        elif action_type == "add_material_slot":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                f"mat = _get_mat('{name}')\n"
                "if obj:\n"
                "    obj.data.materials.append(mat)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} not found.')\n"
            )

        elif action_type == "remove_material_slot":
            slot_idx = int(params.get("slot_index", 0))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                f"    if {slot_idx} < len(obj.material_slots):\n"
                "        bpy.ops.object.select_all(action='DESELECT')\n"
                "        obj.select_set(True)\n"
                "        bpy.context.view_layer.objects.active = obj\n"
                f"        obj.active_material_index = {slot_idx}\n"
                "        bpy.ops.object.material_slot_remove()\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:{slot_idx}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Slot index {slot_idx} out of range.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} not found.')\n"
            )

        elif action_type == "clear_material_slots":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                "    obj.data.materials.clear()\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{obj_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} not found.')\n"
            )

        elif action_type == "get_material_slots":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                "    slots = [m.name if m else None for m in obj.data.materials]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{obj_name}:slots={{slots}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Object {obj_name} not found.')\n"
            )

        # C. PRINCIPLED BSDF
        elif action_type == "set_principled_base_color":
            col = params.get("color", [1.0, 1.0, 1.0, 1.0])
            if isinstance(col, (list, tuple)) and len(col) >= 3:
                r, g, b = max(0.0, min(1.0, float(col[0]))), max(0.0, min(1.0, float(col[1]))), max(0.0, min(1.0, float(col[2])))
                a = max(0.0, min(1.0, float(col[3]))) if len(col) >= 4 else 1.0
                col_tuple = (r, g, b, a)
            else:
                col_tuple = (1.0, 1.0, 1.0, 1.0)
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Base Color', 'BaseColor'], {col_tuple})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{col_tuple}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Base Color socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_metallic":
            val = max(0.0, min(1.0, float(params.get("value", params.get("metallic", 0.0)))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Metallic'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Metallic socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_roughness":
            val = max(0.0, min(1.0, float(params.get("value", params.get("roughness", 0.5)))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Roughness'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Roughness socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_ior":
            val = max(0.001, float(params.get("value", params.get("ior", 1.45))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['IOR'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::IOR socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_transmission":
            val = max(0.0, min(1.0, float(params.get("value", params.get("transmission", params.get("transmission_weight", 0.0))))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Transmission Weight', 'Transmission'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Transmission socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_alpha":
            val = max(0.0, min(1.0, float(params.get("value", params.get("alpha", 1.0)))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Alpha'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Alpha socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_emission":
            col = params.get("color", params.get("emission_color", [1.0, 1.0, 1.0, 1.0]))
            if isinstance(col, (list, tuple)) and len(col) >= 3:
                r, g, b = max(0.0, min(1.0, float(col[0]))), max(0.0, min(1.0, float(col[1]))), max(0.0, min(1.0, float(col[2])))
                a = max(0.0, min(1.0, float(col[3]))) if len(col) >= 4 else 1.0
                col_tuple = (r, g, b, a)
            else:
                col_tuple = (1.0, 1.0, 1.0, 1.0)
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Emission Color', 'Emission'], {col_tuple})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{col_tuple}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Emission socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_emission_strength":
            val = max(0.0, float(params.get("value", params.get("emission_strength", 1.0))))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                "if p:\n"
                f"    ok = _set_socket(p, ['Emission Strength'], {val})\n"
                "    if ok:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{val}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Emission Strength socket not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled BSDF node not found on {name}.')\n"
            )

        elif action_type == "set_principled_normal":
            source_node_name = cls.sanitize_str(params.get("node_name") or params.get("source_node", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "p = _get_principled(mat)\n"
                f"src_node = _get_node(mat, '{source_node_name}')\n"
                "if p and src_node:\n"
                "    out_sock = src_node.outputs.get('Normal') or src_node.outputs.get('Vector') or src_node.outputs[0]\n"
                "    in_sock = p.inputs.get('Normal')\n"
                "    if out_sock and in_sock:\n"
                "        mat.node_tree.links.new(out_sock, in_sock)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{source_node_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Normal sockets not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Principled or Source node {source_node_name} not found.')\n"
            )

        # D. SHADER NODE GRAPH
        elif action_type == "create_shader_node":
            node_type = str(params.get("node_type", "ShaderNodeTexNoise"))
            node_name = cls.sanitize_str(params.get("node_name", ""))
            loc = params.get("location", [0, 0])
            lx, ly = (float(loc[0]), float(loc[1])) if isinstance(loc, (list, tuple)) and len(loc) >= 2 else (0.0, 0.0)

            if node_type not in cls.ALLOWED_NODE_TYPES:
                return f"print('NOVA_ACTION_ERROR::{action_type}::Node type {node_type} is not allowed.')\n"

            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                f"    node = mat.node_tree.nodes.new(type='{node_type}')\n"
                f"    if '{node_name}': node.name = '{node_name}'\n"
                f"    node.location = ({lx}, {ly})\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:' + node.name + ':{node_type}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found or use_nodes disabled.')\n"
            )

        elif action_type == "delete_shader_node":
            node_name = cls.sanitize_str(params.get("node_name", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node:\n"
                "    mat.node_tree.nodes.remove(node)\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Node {node_name} not found.')\n"
            )

        elif action_type == "rename_shader_node":
            node_name = cls.sanitize_str(params.get("node_name", ""))
            new_node_name = cls.sanitize_str(params.get("new_name", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node:\n"
                f"    node.name = '{new_node_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{new_node_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Node {node_name} not found.')\n"
            )

        elif action_type == "set_shader_node_property":
            node_name = cls.sanitize_str(params.get("node_name", ""))
            prop_name = cls.sanitize_str(params.get("property_name", ""))
            val = params.get("value")
            val_code = repr(val)
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node:\n"
                f"    if hasattr(node, '{prop_name}'):\n"
                f"        setattr(node, '{prop_name}', {val_code})\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}:{prop_name}')\n"
                f"    elif '{prop_name}' in node.inputs:\n"
                f"        node.inputs['{prop_name}'].default_value = {val_code}\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}:{prop_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Property or Socket {prop_name} not found on node.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Node {node_name} not found.')\n"
            )

        elif action_type == "connect_shader_nodes":
            from_node = cls.sanitize_str(params.get("from_node", ""))
            from_sock = cls.sanitize_str(params.get("from_socket", "Color"))
            to_node = cls.sanitize_str(params.get("to_node", ""))
            to_sock = cls.sanitize_str(params.get("to_socket", "Base Color"))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"fn = _get_node(mat, '{from_node}')\n"
                f"tn = _get_node(mat, '{to_node}')\n"
                "if mat and fn and tn:\n"
                f"    fs = fn.outputs.get('{from_sock}') or fn.outputs[0]\n"
                f"    ts = tn.inputs.get('{to_sock}') or tn.inputs[0]\n"
                "    if fs and ts:\n"
                "        mat.node_tree.links.new(fs, ts)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{from_node}->{to_node}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Socket {from_sock} or {to_sock} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Nodes {from_node} or {to_node} not found.')\n"
            )

        elif action_type == "disconnect_shader_nodes":
            from_node = cls.sanitize_str(params.get("from_node", ""))
            from_sock = cls.sanitize_str(params.get("from_socket", ""))
            to_node = cls.sanitize_str(params.get("to_node", ""))
            to_sock = cls.sanitize_str(params.get("to_socket", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    removed = False\n"
                "    for link in list(mat.node_tree.links):\n"
                f"        if link.from_node.name == '{from_node}' and link.to_node.name == '{to_node}':\n"
                "            mat.node_tree.links.remove(link)\n"
                "            removed = True\n"
                "    if removed:\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{from_node}->{to_node}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Link between {from_node} and {to_node} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "get_shader_nodes":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    nodes = [{'name': n.name, 'type': n.type} for n in mat.node_tree.nodes]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:count={{len(nodes)}}:nodes={{nodes}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "get_shader_links":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    links = [{'from': l.from_node.name, 'from_socket': l.from_socket.name, 'to': l.to_node.name, 'to_socket': l.to_socket.name} for l in mat.node_tree.links]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:count={{len(links)}}:links={{links}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        # E. PROCEDURAL / TEXTURE NODES
        elif action_type in (
            "add_noise_texture",
            "add_voronoi_texture",
            "add_wave_texture",
            "add_musgrave_or_noise_equivalent",
            "add_color_ramp",
            "add_mapping_node",
            "add_texture_coordinate_node",
            "add_bump_node",
        ):
            node_map = {
                "add_noise_texture": "ShaderNodeTexNoise",
                "add_voronoi_texture": "ShaderNodeTexVoronoi",
                "add_wave_texture": "ShaderNodeTexWave",
                "add_musgrave_or_noise_equivalent": "ShaderNodeTexNoise",
                "add_color_ramp": "ShaderNodeValToRGB",
                "add_mapping_node": "ShaderNodeMapping",
                "add_texture_coordinate_node": "ShaderNodeTexCoord",
                "add_bump_node": "ShaderNodeBump",
            }
            ntype = node_map[action_type]
            node_name = cls.sanitize_str(params.get("node_name", ""))
            loc = params.get("location", [-300, 0])
            lx, ly = (float(loc[0]), float(loc[1])) if isinstance(loc, (list, tuple)) and len(loc) >= 2 else (-300.0, 0.0)

            # Property configuration strings
            prop_lines = []
            if "scale" in params:
                prop_lines.append(f"    _set_socket(node, ['Scale'], {float(params['scale'])})\n")
            if "detail" in params:
                prop_lines.append(f"    _set_socket(node, ['Detail'], {float(params['detail'])})\n")
            if "roughness" in params:
                prop_lines.append(f"    _set_socket(node, ['Roughness'], {float(params['roughness'])})\n")
            if "distortion" in params:
                prop_lines.append(f"    _set_socket(node, ['Distortion'], {float(params['distortion'])})\n")
            if "strength" in params and ntype == "ShaderNodeBump":
                prop_lines.append(f"    _set_socket(node, ['Strength'], {max(0.0, min(1.0, float(params['strength'])))})\n")
            if "distance" in params and ntype == "ShaderNodeBump":
                prop_lines.append(f"    _set_socket(node, ['Distance'], {max(0.0, float(params['distance']))})\n")

            props_code = "".join(prop_lines)

            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                f"    node = mat.node_tree.nodes.new(type='{ntype}')\n"
                f"    if '{node_name}': node.name = '{node_name}'\n"
                f"    node.location = ({lx}, {ly})\n"
                + props_code +
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:' + node.name)\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "connect_texture_to_material":
            tex_name = cls.sanitize_str(params.get("texture_node_name", ""))
            target_input = cls.sanitize_str(params.get("target_input") or params.get("socket_name", "Base Color"))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"tex_node = _get_node(mat, '{tex_name}')\n"
                "p = _get_principled(mat)\n"
                "if mat and tex_node and p:\n"
                "    out_sock = tex_node.outputs.get('Color') or tex_node.outputs.get('Fac') or tex_node.outputs[0]\n"
                f"    in_sock = p.inputs.get('{target_input}')\n"
                "    if not in_sock:\n"
                f"        cl = '{target_input}'.lower().replace(' ', '').replace('_', '')\n"
                "        for inp in p.inputs:\n"
                "            if cl in inp.name.lower().replace(' ', '').replace('_', ''):\n"
                "                in_sock = inp\n"
                "                break\n"
                "    if out_sock and in_sock:\n"
                "        mat.node_tree.links.new(out_sock, in_sock)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{tex_name}->{target_input}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Target socket {target_input} not found on Principled BSDF.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Texture node {tex_name} not found.')\n"
            )

        # F. IMAGE TEXTURE SUPPORT
        elif action_type == "add_image_texture":
            img_path = cls.sanitize_str(params.get("image_path", ""))
            node_name = cls.sanitize_str(params.get("node_name", ""))
            loc = params.get("location", [-400, 0])
            lx, ly = (float(loc[0]), float(loc[1])) if isinstance(loc, (list, tuple)) and len(loc) >= 2 else (-400.0, 0.0)

            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')\n"
                f"    if '{node_name}': node.name = '{node_name}'\n"
                f"    node.location = ({lx}, {ly})\n"
                f"    if os.path.exists('{img_path}'):\n"
                f"        img = bpy.data.images.load(filepath='{img_path}')\n"
                "        node.image = img\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:' + node.name + ':{img_path}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Image path {img_path} does not exist.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "set_image_texture_path":
            img_path = cls.sanitize_str(params.get("image_path", ""))
            node_name = cls.sanitize_str(params.get("node_name", ""))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node and node.type == 'TEX_IMAGE':\n"
                f"    if os.path.exists('{img_path}'):\n"
                f"        img = bpy.data.images.load(filepath='{img_path}')\n"
                "        node.image = img\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Image path {img_path} does not exist.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Image Texture node {node_name} not found.')\n"
            )

        elif action_type == "set_image_texture_interpolation":
            node_name = cls.sanitize_str(params.get("node_name", ""))
            raw_interp = str(params.get("interpolation", "Linear")).upper()
            if raw_interp not in ("LINEAR", "CLOSEST", "CUBIC", "SMART"):
                raw_interp = "LINEAR"
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node and node.type == 'TEX_IMAGE':\n"
                "    try:\n"
                f"        node.interpolation = '{raw_interp}'\n"
                "    except TypeError:\n"
                f"        node.interpolation = '{raw_interp.title()}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}:{raw_interp}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Image Texture node {node_name} not found.')\n"
            )

        elif action_type == "set_image_texture_extension":
            node_name = cls.sanitize_str(params.get("node_name", ""))
            raw_ext = str(params.get("extension", "REPEAT")).upper()
            if raw_ext not in ("REPEAT", "EXTEND", "CLIP", "MIRROR"):
                raw_ext = "REPEAT"
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"node = _get_node(mat, '{node_name}')\n"
                "if mat and node and node.type == 'TEX_IMAGE':\n"
                "    try:\n"
                f"        node.extension = '{raw_ext}'\n"
                "    except TypeError:\n"
                f"        node.extension = '{raw_ext.title()}'\n"
                f"    print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{node_name}:{raw_ext}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Image Texture node {node_name} not found.')\n"
            )

        elif action_type == "connect_image_texture_to_shader":
            img_node_name = cls.sanitize_str(params.get("image_node_name", ""))
            shader_node_name = cls.sanitize_str(params.get("shader_node_name", ""))
            sock_name = cls.sanitize_str(params.get("socket_name", "Base Color"))
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                f"img_node = _get_node(mat, '{img_node_name}')\n"
                f"shader_node = _get_node(mat, '{shader_node_name}') or _get_principled(mat)\n"
                "if mat and img_node and shader_node:\n"
                "    out_sock = img_node.outputs.get('Color') or img_node.outputs[0]\n"
                f"    in_sock = shader_node.inputs.get('{sock_name}')\n"
                "    if not in_sock:\n"
                f"        cl = '{sock_name}'.lower().replace(' ', '').replace('_', '')\n"
                "        for inp in shader_node.inputs:\n"
                "            if cl in inp.name.lower().replace(' ', '').replace('_', ''):\n"
                "                in_sock = inp\n"
                "                break\n"
                "    if out_sock and in_sock:\n"
                "        mat.node_tree.links.new(out_sock, in_sock)\n"
                f"        print('NOVA_ACTION_SUCCESS::{action_type}::{name}:{img_node_name}->{sock_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Sockets not found for connection.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} or Image node {img_node_name} not found.')\n"
            )

        # G. INSPECTION / VALIDATION
        elif action_type == "get_material_state":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat:\n"
                "    p = _get_principled(mat)\n"
                "    nodes_cnt = len(mat.node_tree.nodes) if mat.use_nodes else 0\n"
                "    links_cnt = len(mat.node_tree.links) if mat.use_nodes else 0\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:nodes={{nodes_cnt}}:links={{links_cnt}}:principled={{bool(p)}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "get_material_node_tree":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    nodes = [n.name for n in mat.node_tree.nodes]\n"
                "    links = [f'{l.from_node.name}->{l.to_node.name}' for l in mat.node_tree.links]\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:nodes={{nodes}}:links={{links}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "validate_material":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    has_out = any(n.type == 'OUTPUT_MATERIAL' for n in mat.node_tree.nodes)\n"
                "    has_p = any(n.type == 'BSDF_PRINCIPLED' for n in mat.node_tree.nodes)\n"
                "    valid = has_out and has_p\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:valid={{valid}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        elif action_type == "validate_shader_links":
            return (
                header +
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"mat = _get_mat('{name}')\n"
                "if mat and mat.use_nodes:\n"
                "    valid_links = len(mat.node_tree.links) > 0\n"
                f"    print(f'NOVA_ACTION_SUCCESS::{action_type}::{name}:valid_links={{valid_links}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Material {name} not found.')\n"
            )

        raise ValueError(f"Action '{action_type}' not supported by BlenderMaterialExecutor.")


SUPPORTED_MATERIAL_ACTIONS = {
    "create_material", "delete_material", "rename_material", "get_material", "get_materials",
    "assign_material", "remove_material", "add_material_slot", "remove_material_slot", "clear_material_slots", "get_material_slots",
    "set_principled_base_color", "set_principled_metallic", "set_principled_roughness", "set_principled_ior", "set_principled_transmission",
    "set_principled_alpha", "set_principled_emission", "set_principled_emission_strength", "set_principled_normal",
    "create_shader_node", "delete_shader_node", "rename_shader_node", "set_shader_node_property", "connect_shader_nodes",
    "disconnect_shader_nodes", "get_shader_nodes", "get_shader_links",
    "add_noise_texture", "add_voronoi_texture", "add_wave_texture", "add_musgrave_or_noise_equivalent", "add_color_ramp",
    "add_mapping_node", "add_texture_coordinate_node", "add_bump_node", "connect_texture_to_material",
    "add_image_texture", "set_image_texture_path", "set_image_texture_interpolation", "set_image_texture_extension",
    "connect_image_texture_to_shader",
    "get_material_state", "get_material_node_tree", "validate_material", "validate_shader_links",
}
