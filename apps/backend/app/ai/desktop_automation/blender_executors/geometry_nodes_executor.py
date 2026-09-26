"""Blender Geometry Nodes Domain Executor.

Generates BPY scripts for node group lifecycle, node addition/removal,
Blender 5.2 tree.interface socket management, node linking, property editing,
geometry node modifier assignment, graph validation, and evaluated geometry inspection.
"""

from typing import Any, Dict, Set

ALLOWED_NODE_TYPES: Set[str] = {
    "GeometryNodeMeshCube",
    "GeometryNodeMeshUVSphere",
    "GeometryNodeTransform",
    "GeometryNodeSetPosition",
    "GeometryNodeJoinGeometry",
    "GeometryNodeMeshToCurve",
    "GeometryNodeCurveToMesh",
    "GeometryNodeStoreNamedAttribute",
    "GeometryNodeInputSceneTime",
    "NodeGroupInput",
    "NodeGroupOutput",
}

ALLOWED_SOCKET_TYPES: Set[str] = {
    "NodeSocketGeometry",
    "NodeSocketFloat",
    "NodeSocketInt",
    "NodeSocketVector",
    "NodeSocketColor",
    "NodeSocketBoolean",
    "NodeSocketString",
}

SUPPORTED_GEOMETRY_NODES_ACTIONS: Set[str] = {
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
}


class BlenderGeometryNodesExecutor:
    """Domain executor for Blender Geometry Nodes operations."""

    @classmethod
    def build_script(cls, action_type: str, params: Dict[str, Any]) -> str:
        """Constructs BPY script for Geometry Nodes actions."""
        if action_type not in SUPPORTED_GEOMETRY_NODES_ACTIONS:
            raise ValueError(f"Unsupported geometry nodes action: '{action_type}'")

        if action_type == "create_geometry_node_group":
            name = params.get("name") or params.get("group_name") or "Geometry Nodes"
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::create_geometry_node_group')\n"
                f"group_name = '{name}'\n"
                "group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')\n"
                "group.use_fake_user = True\n"
                "# Auto create Group Input and Group Output nodes if not present\n"
                "if 'Group Input' not in group.nodes:\n"
                "    group.nodes.new('NodeGroupInput')\n"
                "if 'Group Output' not in group.nodes:\n"
                "    group.nodes.new('NodeGroupOutput')\n"
                f"print(f'NOVA_ACTION_SUCCESS::create_geometry_node_group::{{group.name}}')\n"
            )

        elif action_type == "delete_geometry_node_group":
            name = params["name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::delete_geometry_node_group')\n"
                f"group = bpy.data.node_groups.get('{name}')\n"
                "if group:\n"
                "    bpy.data.node_groups.remove(group)\n"
                f"    print('NOVA_ACTION_SUCCESS::delete_geometry_node_group::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::delete_geometry_node_group::Group {name} not found.')\n"
            )

        elif action_type == "rename_geometry_node_group":
            name = params["name"]
            new_name = params["new_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::rename_geometry_node_group')\n"
                f"group = bpy.data.node_groups.get('{name}')\n"
                "if group:\n"
                f"    group.name = '{new_name}'\n"
                f"    print('NOVA_ACTION_SUCCESS::rename_geometry_node_group::{new_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::rename_geometry_node_group::Group {name} not found.')\n"
            )

        elif action_type == "get_geometry_node_groups":
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_node_groups')\n"
                "gn_groups = [g.name for g in bpy.data.node_groups if g.type == 'GeometryNodeTree']\n"
                "print('GROUPS_JSON:' + json.dumps(gn_groups))\n"
                "print('NOVA_ACTION_SUCCESS::get_geometry_node_groups::' + str(len(gn_groups)))\n"
            )

        elif action_type == "get_geometry_node_group_state":
            name = params["name"]
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_node_group_state')\n"
                f"group = bpy.data.node_groups.get('{name}')\n"
                "if group:\n"
                "    nodes = [n.name for n in group.nodes]\n"
                "    links_count = len(group.links)\n"
                "    info = {'name': group.name, 'nodes': nodes, 'links_count': links_count}\n"
                "    print('GROUP_STATE_JSON:' + json.dumps(info))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_geometry_node_group_state::{name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_node_group_state::Group {name} not found.')\n"
            )

        elif action_type == "add_geometry_nodes_modifier":
            obj_name = params.get("object_name") or params.get("name", "Cube")
            mod_name = params.get("modifier_name", "GeometryNodes")
            group_name = params.get("group_name")
            grp_assign = f"grp = bpy.data.node_groups.get('{group_name}')\nif grp:\n    mod.node_group = grp\n" if group_name else ""
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_geometry_nodes_modifier')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.new(name='{mod_name}', type='NODES')\n"
                f"    {grp_assign}"
                f"    print('NOVA_ACTION_SUCCESS::add_geometry_nodes_modifier::{mod_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_geometry_nodes_modifier::Object {obj_name} not found.')\n"
            )

        elif action_type == "remove_geometry_nodes_modifier":
            obj_name = params.get("object_name") or params.get("name", "Cube")
            mod_name = params.get("modifier_name", "GeometryNodes")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_geometry_nodes_modifier')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                f"    mod = obj.modifiers.get('{mod_name}')\n"
                "    if mod:\n"
                "        obj.modifiers.remove(mod)\n"
                f"        print('NOVA_ACTION_SUCCESS::remove_geometry_nodes_modifier::{mod_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::remove_geometry_nodes_modifier::Modifier {mod_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_geometry_nodes_modifier::Object {obj_name} not found.')\n"
            )

        elif action_type == "assign_geometry_node_group":
            obj_name = params.get("object_name") or params.get("name", "Cube")
            mod_name = params.get("modifier_name", "GeometryNodes")
            group_name = params["group_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::assign_geometry_node_group')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                f"grp = bpy.data.node_groups.get('{group_name}')\n"
                "if obj and grp:\n"
                f"    mod = obj.modifiers.get('{mod_name}') or obj.modifiers.new(name='{mod_name}', type='NODES')\n"
                "    mod.node_group = grp\n"
                f"    print('NOVA_ACTION_SUCCESS::assign_geometry_node_group::{group_name}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::assign_geometry_node_group::Object or Group not found.')\n"
            )

        elif action_type == "get_geometry_nodes_modifiers":
            obj_name = params.get("object_name") or params.get("name", "Cube")
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_nodes_modifiers')\n"
                f"obj = bpy.data.objects.get('{obj_name}')\n"
                "if obj:\n"
                "    mods = [m.name for m in obj.modifiers if m.type == 'NODES']\n"
                "    print('MODIFIERS_JSON:' + json.dumps(mods))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_geometry_nodes_modifiers::' + str(len(mods)))\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_nodes_modifiers::Object {obj_name} not found.')\n"
            )

        elif action_type == "create_geometry_node":
            group_name = params["group_name"]
            node_type = params["node_type"]
            node_name = params.get("node_name") or params.get("name")
            name_assign = f"node.name = '{node_name}'\n" if node_name else ""
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::create_geometry_node')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                "    try:\n"
                f"        node = group.nodes.new(type='{node_type}')\n"
                f"        {name_assign}"
                f"        print('NOVA_ACTION_SUCCESS::create_geometry_node::' + node.name)\n"
                "    except Exception as e:\n"
                f"        print('NOVA_ACTION_ERROR::create_geometry_node::Failed creating {node_type}: ' + str(e))\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::create_geometry_node::Group {group_name} not found.')\n"
            )

        elif action_type == "delete_geometry_node":
            group_name = params["group_name"]
            node_name = params["node_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::delete_geometry_node')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                "        group.nodes.remove(node)\n"
                f"        print('NOVA_ACTION_SUCCESS::delete_geometry_node::{node_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::delete_geometry_node::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::delete_geometry_node::Group {group_name} not found.')\n"
            )

        elif action_type == "rename_geometry_node":
            group_name = params["group_name"]
            node_name = params["node_name"]
            new_name = params["new_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::rename_geometry_node')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                f"        node.name = '{new_name}'\n"
                f"        print('NOVA_ACTION_SUCCESS::rename_geometry_node::{new_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::rename_geometry_node::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::rename_geometry_node::Group {group_name} not found.')\n"
            )

        elif action_type == "duplicate_geometry_node":
            group_name = params["group_name"]
            node_name = params["node_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::duplicate_geometry_node')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    src_node = group.nodes.get('{node_name}')\n"
                "    if src_node:\n"
                "        new_node = group.nodes.new(type=src_node.bl_idname)\n"
                "        new_node.location = (src_node.location.x + 40, src_node.location.y - 40)\n"
                f"        print('NOVA_ACTION_SUCCESS::duplicate_geometry_node::' + new_node.name)\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::duplicate_geometry_node::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::duplicate_geometry_node::Group {group_name} not found.')\n"
            )

        elif action_type == "get_geometry_nodes":
            group_name = params["group_name"]
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_nodes')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                "    nodes = [{'name': n.name, 'type': n.bl_idname} for n in group.nodes]\n"
                "    print('NODES_JSON:' + json.dumps(nodes))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_geometry_nodes::' + str(len(nodes)))\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_nodes::Group {group_name} not found.')\n"
            )

        elif action_type == "get_geometry_node_state":
            group_name = params["group_name"]
            node_name = params["node_name"]
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_node_state')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                "        inputs = [i.name for i in node.inputs]\n"
                "        outputs = [o.name for o in node.outputs]\n"
                "        info = {'name': node.name, 'type': node.bl_idname, 'inputs': inputs, 'outputs': outputs}\n"
                "        print('NODE_STATE_JSON:' + json.dumps(info))\n"
                f"        print('NOVA_ACTION_SUCCESS::get_geometry_node_state::{node_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::get_geometry_node_state::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_node_state::Group {group_name} not found.')\n"
            )

        elif action_type == "set_geometry_node_location":
            group_name = params["group_name"]
            node_name = params["node_name"]
            x = params["x"]
            y = params["y"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::set_geometry_node_location')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                f"        node.location = ({x}, {y})\n"
                f"        print('NOVA_ACTION_SUCCESS::set_geometry_node_location::{x},{y}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::set_geometry_node_location::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::set_geometry_node_location::Group {group_name} not found.')\n"
            )

        elif action_type in ("set_geometry_node_property", "set_geometry_node_input"):
            group_name = params["group_name"]
            node_name = params["node_name"]
            input_identifier = params.get("input_name") or params.get("property") or params.get("input_index", 0)
            val = params["value"]
            val_code = f"({val[0]}, {val[1]}, {val[2]})" if isinstance(val, (list, tuple)) and len(val) == 3 else (f"'{val}'" if isinstance(val, str) else str(val))
            idx_expr = f"'{input_identifier}'" if isinstance(input_identifier, str) else str(input_identifier)
            return (
                "import bpy\n"
                f"print('NOVA_ACTION_START::{action_type}')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                f"        inp = node.inputs.get({idx_expr}) if isinstance({idx_expr}, str) else node.inputs[{idx_expr}]\n"
                "        if inp:\n"
                f"            inp.default_value = {val_code}\n"
                f"            print('NOVA_ACTION_SUCCESS::{action_type}::{node_name}')\n"
                "        else:\n"
                f"            print('NOVA_ACTION_ERROR::{action_type}::Input {input_identifier} not found.')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::{action_type}::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::{action_type}::Group {group_name} not found.')\n"
            )

        elif action_type == "get_geometry_node_input":
            group_name = params["group_name"]
            node_name = params["node_name"]
            input_name = params["input_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::get_geometry_node_input')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                f"        inp = node.inputs.get('{input_name}')\n"
                "        if inp:\n"
                "            val = str(getattr(inp, 'default_value', None))\n"
                "            print(f'NOVA_ACTION_SUCCESS::get_geometry_node_input::{val}')\n"
                "        else:\n"
                f"            print('NOVA_ACTION_ERROR::get_geometry_node_input::Input {input_name} not found.')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::get_geometry_node_input::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_node_input::Group {group_name} not found.')\n"
            )

        elif action_type == "get_geometry_node_outputs":
            group_name = params["group_name"]
            node_name = params["node_name"]
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_node_outputs')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node = group.nodes.get('{node_name}')\n"
                "    if node:\n"
                "        outs = [o.name for o in node.outputs]\n"
                "        print('OUTPUTS_JSON:' + json.dumps(outs))\n"
                f"        print('NOVA_ACTION_SUCCESS::get_geometry_node_outputs::' + str(len(outs)))\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::get_geometry_node_outputs::Node {node_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_node_outputs::Group {group_name} not found.')\n"
            )

        elif action_type == "connect_geometry_nodes":
            group_name = params["group_name"]
            from_node = params["from_node"]
            from_socket = params.get("from_socket", 0)
            to_node = params["to_node"]
            to_socket = params.get("to_socket", 0)
            f_sock_expr = f"'{from_socket}'" if isinstance(from_socket, str) else str(from_socket)
            t_sock_expr = f"'{to_socket}'" if isinstance(to_socket, str) else str(to_socket)
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::connect_geometry_nodes')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                f"    node_a = group.nodes.get('{from_node}')\n"
                f"    node_b = group.nodes.get('{to_node}')\n"
                "    if node_a and node_b:\n"
                f"        out_sock = node_a.outputs.get({f_sock_expr}) if isinstance({f_sock_expr}, str) else node_a.outputs[{f_sock_expr}]\n"
                f"        in_sock = node_b.inputs.get({t_sock_expr}) if isinstance({t_sock_expr}, str) else node_b.inputs[{t_sock_expr}]\n"
                "        if out_sock and in_sock:\n"
                "            group.links.new(out_sock, in_sock)\n"
                f"            print('NOVA_ACTION_SUCCESS::connect_geometry_nodes::{from_node}->{to_node}')\n"
                "        else:\n"
                "            print('NOVA_ACTION_ERROR::connect_geometry_nodes::Socket missing.')\n"
                "    else:\n"
                "        print('NOVA_ACTION_ERROR::connect_geometry_nodes::Node missing.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::connect_geometry_nodes::Group {group_name} not found.')\n"
            )

        elif action_type == "disconnect_geometry_nodes":
            group_name = params["group_name"]
            from_node = params["from_node"]
            to_node = params["to_node"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::disconnect_geometry_nodes')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                "    removed = 0\n"
                "    for link in list(group.links):\n"
                f"        if link.from_node.name == '{from_node}' and link.to_node.name == '{to_node}':\n"
                "            group.links.remove(link)\n"
                "            removed += 1\n"
                f"    print(f'NOVA_ACTION_SUCCESS::disconnect_geometry_nodes::{{removed}}')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::disconnect_geometry_nodes::Group {group_name} not found.')\n"
            )

        elif action_type == "get_geometry_node_links":
            group_name = params["group_name"]
            return (
                "import bpy, json\n"
                "print('NOVA_ACTION_START::get_geometry_node_links')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                "    links = [{'from': l.from_node.name, 'to': l.to_node.name} for l in group.links]\n"
                "    print('LINKS_JSON:' + json.dumps(links))\n"
                f"    print('NOVA_ACTION_SUCCESS::get_geometry_node_links::' + str(len(links)))\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::get_geometry_node_links::Group {group_name} not found.')\n"
            )

        elif action_type == "add_geometry_node_socket":
            group_name = params["group_name"]
            socket_name = params["socket_name"]
            in_out = params.get("in_out", "INPUT").upper()
            socket_type = params.get("socket_type", "NodeSocketGeometry")
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::add_geometry_node_socket')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group:\n"
                "    # Blender 5.2 tree.interface API\n"
                "    if hasattr(group, 'interface'):\n"
                f"        sock = group.interface.new_socket(name='{socket_name}', in_out='{in_out}', socket_type='{socket_type}')\n"
                f"        print('NOVA_ACTION_SUCCESS::add_geometry_node_socket::{socket_name}')\n"
                "    else:\n"
                "        print('NOVA_ACTION_ERROR::add_geometry_node_socket::Group missing interface API')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::add_geometry_node_socket::Group {group_name} not found.')\n"
            )

        elif action_type == "remove_geometry_node_socket":
            group_name = params["group_name"]
            socket_name = params["socket_name"]
            return (
                "import bpy\n"
                "print('NOVA_ACTION_START::remove_geometry_node_socket')\n"
                f"group = bpy.data.node_groups.get('{group_name}')\n"
                "if group and hasattr(group, 'interface'):\n"
                "    found = None\n"
                "    for item in group.interface.items_tree:\n"
                f"        if item.name == '{socket_name}':\n"
                "            found = item\n"
                "            break\n"
                "    if found:\n"
                "        group.interface.remove(found)\n"
                f"        print('NOVA_ACTION_SUCCESS::remove_geometry_node_socket::{socket_name}')\n"
                "    else:\n"
                f"        print('NOVA_ACTION_ERROR::remove_geometry_node_socket::Socket {socket_name} not found.')\n"
                "else:\n"
                f"    print('NOVA_ACTION_ERROR::remove_geometry_node_socket::Group {group_name} not found.')\n"
            )

        raise ValueError(f"No BPY template for action '{action_type}'")
